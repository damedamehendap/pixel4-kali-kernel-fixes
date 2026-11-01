#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import os,ctypes,struct,json
lib=ctypes.CDLL(None,use_errno=True);lib.syscall.restype=ctypes.c_long
results={}
# Run PID namespace changes only inside a disposable child process.
r,w=os.pipe();pid=os.fork()
if pid==0:
 os.close(r)
 rc=lib.syscall(97,0x20000000)
 if rc: os.write(w,json.dumps({'unshare':rc,'errno':ctypes.get_errno()}).encode());os._exit(1)
 child=os.fork()
 if child==0:
  os.write(w,json.dumps({'unshare':0,'child_pid':os.getpid(),'pass':os.getpid()==1}).encode());os._exit(0)
 _,status=os.waitpid(child,0);os._exit(os.waitstatus_to_exitcode(status))
os.close(w);data=os.read(r,4096);os.close(r);_,status=os.waitpid(pid,0)
results['pid_namespace']=json.loads(data);results['pid_namespace']['exit']=os.waitstatus_to_exitcode(status)
mounts=[]
with open('/proc/self/mountinfo') as f:
 for line in f:
  fields=line.split();mounts.append((fields[4],int(fields[0])))
checks=[]
for path in ['/','/proc','/sys','/dev']:
 exact=[mid for mp,mid in mounts if mp==path]
 if not exact:continue
 buf=ctypes.create_string_buffer(256)
 rc=lib.syscall(291,-100,ctypes.c_char_p(path.encode()),0,0x17ff,buf)
 mask=struct.unpack_from('<I',buf.raw,0)[0];mnt=struct.unpack_from('<Q',buf.raw,0x90)[0]
 checks.append(dict(path=path,rc=rc,errno=ctypes.get_errno() if rc else 0,mask=hex(mask),mnt_id=mnt,mountinfo_ids=exact,passed=rc==0 and bool(mask&0x1000) and mnt in exact))
results['statx']=checks
results['pass']=results['pid_namespace'].get('pass',False) and bool(checks) and all(c['passed'] for c in checks)
print(json.dumps(results,indent=2),flush=True)
raise SystemExit(0 if results['pass'] else 1)
