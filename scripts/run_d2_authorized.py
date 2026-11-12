#!/usr/bin/env python3
"""D2 runner using only passwordless `mn` and `ovs-ofctl` privileges."""
from __future__ import annotations
import os, pathlib, re, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parents[1]; E=ROOT/'evidence'
MN=['sudo','-n','/usr/bin/mn','--custom',str(ROOT/'topology/redundant_topology.py'),'--topo','redundanttransfer','--controller','remote,ip=127.0.0.1,port=6653','--switch','ovs,protocols=OpenFlow13','--mac','--arp']
OVS=['sudo','-n','/usr/bin/ovs-ofctl','-O','OpenFlow13','dump-flows','s1']
def run(cmd, **kw): return subprocess.run(cmd,check=True,timeout=kw.pop('timeout',20),**kw)
def main():
    E.mkdir(exist_ok=True)
    # Validate sudo scope before creating *any* virtual interface.
    run(['sudo','-n','/usr/bin/mn','--version'],capture_output=True,text=True)
    ctl_log=open(E/'d2_controller.log','w'); ctl=subprocess.Popen([os.environ['OSKEN_PYTHON'],str(ROOT/'controller/launch.py')],cwd=ROOT,stdout=ctl_log,stderr=subprocess.STDOUT)
    mn_log=open(E/'d2_mininet.log','w'); mn=None
    try:
        time.sleep(2); mn=subprocess.Popen(MN,stdin=subprocess.PIPE,stdout=mn_log,stderr=subprocess.STDOUT,text=True)
        def cmd(text): mn.stdin.write(text+'\n'); mn.stdin.flush(); time.sleep(.35)
        time.sleep(3)
        # The sole mutable link is named Mininet switch-to-switch link, never enp0s1.
        cmd('h2 mkdir -p /tmp/d2_received')
        cmd('h2 python3 -u %s --host 10.0.0.2 --port 5055 --out /tmp/d2_received > %s 2>&1 &'%(ROOT/'receiver/udp_receiver.py',E/'d2_receiver.log'))
        cmd('h1 dd if=/dev/urandom of=/tmp/d2_source.bin bs=1M count=128 status=none')
        cmd('h1 python3 -u %s /tmp/d2_source.bin --host 10.0.0.2 --port 5055 > %s 2>&1 &'%(ROOT/'sender/udp_sender.py',E/'d2_sender.log'))
        time.sleep(.25); (E/'d2_flows_before.txt').write_text(run(OVS,capture_output=True,text=True).stdout)
        cmd('link s1 s2 down')
        time.sleep(25); (E/'d2_flows_after.txt').write_text(run(OVS,capture_output=True,text=True).stdout)
        cmd('h1 sha256sum /tmp/d2_source.bin'); cmd('h2 sha256sum /tmp/d2_received/d2_source.bin'); cmd('exit')
        mn.wait(timeout=20); mn=None
    finally:
        if mn and mn.poll() is None:
            mn.stdin.write('exit\n'); mn.stdin.flush(); mn.wait(timeout=20)
        ctl.terminate(); ctl.wait(timeout=5); ctl_log.close(); mn_log.close()
    sender=(E/'d2_sender.log').read_text(errors='replace'); receiver=(E/'d2_receiver.log').read_text(errors='replace'); controller=(E/'d2_controller.log').read_text(errors='replace')
    sh=re.findall(r'SHA-256: ([a-f0-9]{64})',sender); rh=re.findall(r'SHA-256: ([a-f0-9]{64})',receiver)
    ok=bool(sh and rh and sh[-1]==rh[-1] and 'Integrity check: PASS' in sender and 'PRIMARY LINK FAILURE' in controller)
    (E/'d2_result.txt').write_text('failed_link=s1-s2 (Mininet virtual link only)\nsource_sha256=%s\ndestination_sha256=%s\ncontroller_failover=%s\nPASS=%s\n'%((sh[-1] if sh else ''),(rh[-1] if rh else ''),'PRIMARY LINK FAILURE' in controller,ok))
    print('D2 PRACTICAL:', 'PASS' if ok else 'FAIL'); return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
