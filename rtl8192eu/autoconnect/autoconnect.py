#!/usr/bin/python3
"""Manage only the RTL8192EU USB interface. Never changes Android's default route."""
import hashlib, ipaddress, json, os, signal, subprocess, sys, time
import xml.etree.ElementTree as ET
from pathlib import Path

BASE=Path('/run/rtl8192eu-autoconnect')
TABLE='19292'
PRIORITY='11992'
SOURCE='YOUR_SAVED_WIFI_SSID'
TARGET='YOUR_2_4_GHZ_WIFI_SSID'
ENV={**os.environ,'PATH':'/usr/sbin:/usr/bin:/sbin:/bin'}
stopping=False

def run(*args,check=False):
 return subprocess.run(args,env=ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15,check=check)

def log(message):
 print(time.strftime('%Y-%m-%d %H:%M:%S'),message,flush=True)

def find_interface():
 for net in Path('/sys/class/net').iterdir():
  driver=net/'device/driver'
  if driver.exists() and driver.resolve().name=='rtl8192eu':
   return net.name
 return None

def status(state,iface=None):
 (BASE/'status.json').write_text(json.dumps({'state':state,'interface':iface}))

def stop(sig,frame):
 global stopping
 stopping=True

class Connection:
 def __init__(self,iface,key):
  self.iface=iface; self.children=[]; self.source=None; self.rule=False; self.started=time.monotonic()
  self.config=BASE/'wpa.conf'
  psk=hashlib.pbkdf2_hmac('sha1',key.encode(),TARGET.encode(),4096,32).hex()
  self.config.write_text('ctrl_interface='+str(BASE/'ctrl')+'\nupdate_config=0\nnetwork={\n ssid="'+TARGET+'"\n psk='+psk+'\n key_mgmt=WPA-PSK\n scan_ssid=1\n}\n')
  (BASE/'dhcpcd.conf').write_text('noipv6\nnogateway\nnohook resolv.conf,hostname,ntp.conf\n')
 def start(self):
  run('ip','link','set',self.iface,'up',check=True)
  self.children.append(subprocess.Popen(['wpa_supplicant','-Dnl80211','-i'+self.iface,'-c'+str(self.config)],env=ENV,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True))
  status('authenticating',self.iface)
 def poll(self):
  if any(p.poll() is not None for p in self.children):
   raise RuntimeError('Connection helper exited')
  s=run('wpa_cli','-p'+str(BASE/'ctrl'),'-i'+self.iface,'status').stdout
  if 'wpa_state=COMPLETED' not in s:
   if time.monotonic()-self.started>90: raise RuntimeError('Authentication timed out')
   return
  if len(self.children)==1:
   self.children.append(subprocess.Popen(['dhcpcd','-B','-4','-G','-f',str(BASE/'dhcpcd.conf'),'-c','/opt/rtl8192eu-autoconnect/dhcp-hook.sh','-t','30',self.iface],env=ENV,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True))
   status('obtaining_address',self.iface)
  info=json.loads(run('ip','-j','-4','addr','show','dev',self.iface).stdout or '[]')
  addrs=[a for i in info for a in i.get('addr_info',[]) if a.get('scope')=='global']
  if addrs and not self.source:
   self.source=addrs[0]['local']
   lease=BASE/'lease'
   values=lease.read_text().splitlines() if lease.exists() else []
   routers=values[1].split() if len(values)>1 and values[0]==self.source else []
   if not routers:
    self.source=None; return
   gateway=str(ipaddress.IPv4Address(routers[0]))
   network=str(ipaddress.IPv4Network(self.source+'/'+str(addrs[0]['prefixlen']),strict=False))
   run('ip','route','add','table',TABLE,network,'dev',self.iface,'src',self.source,check=True)
   run('ip','route','add','table',TABLE,'default','via',gateway,'dev',self.iface,check=True)
   run('ip','rule','add','priority',PRIORITY,'from',self.source+'/32','lookup',TABLE,check=True)
   self.rule=True
   status('connected',self.iface); log('External Wi-Fi connected: '+self.iface)
 def close(self):
  # Only processes launched by this supervisor are terminated.
  for p in reversed(self.children):
   if p.poll() is None:
    p.terminate()
    try: p.wait(timeout=8)
    except subprocess.TimeoutExpired:
     os.killpg(p.pid,signal.SIGKILL); p.wait()
  if self.rule:
   run('ip','rule','del','priority',PRIORITY,'from',self.source+'/32','lookup',TABLE)
  run('ip','route','flush','table',TABLE)
  if self.source and (Path('/sys/class/net')/self.iface).exists():
   run('ip','addr','flush','dev',self.iface,'scope','global')
  if (Path('/sys/class/net')/self.iface).exists():
   run('ip','link','set',self.iface,'down')
  self.config.unlink(missing_ok=True)
  (BASE/'lease').unlink(missing_ok=True)
  status('waiting_for_adapter')

def main():
 os.umask(0o077); BASE.mkdir(mode=0o700,exist_ok=True)
 import fcntl
 lock=(BASE/'supervisor.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 # Refuse to overwrite routing state owned by another program.
 if run('ip','route','show','table',TABLE).stdout.strip() or any(l.startswith(PRIORITY+':') for l in run('ip','rule').stdout.splitlines()):
  raise RuntimeError('Reserved routing slot is already in use')
 tree=ET.parse(sys.stdin); key=None
 for w in tree.findall('.//Network/WifiConfiguration'):
  d={x.get('name'):x.text for x in w}
  if d.get('SSID')==json.dumps(SOURCE):
   raw=d.get('PreSharedKey') or ''
   if raw.startswith('"'): key=json.loads(raw)
 if key is None: raise RuntimeError('Reusable home Wi-Fi credential unavailable')
 signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
 connection=None; retry_at=0
 status('waiting_for_adapter'); log('Waiting for external adapter')
 try:
  while not stopping:
   iface=find_interface()
   if connection and connection.iface!=iface:
    connection.close(); connection=None
   if iface and connection is None and time.monotonic()>=retry_at:
    try:
     connection=Connection(iface,key); connection.start()
    except Exception:
     if connection: connection.close()
     connection=None; retry_at=time.monotonic()+30; log('Start failed; retry delayed')
   if connection:
    try: connection.poll()
    except Exception:
     connection.close(); connection=None; retry_at=time.monotonic()+30; log('Connection failed; retry delayed')
   time.sleep(3)
 finally:
  if connection: connection.close()
  status('stopped')

if __name__=='__main__': main()
