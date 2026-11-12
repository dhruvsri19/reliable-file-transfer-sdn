#!/usr/bin/env python3
"""Real D2 integration: fail s1-s2 during one UDP transfer and verify its hash."""
import os, pathlib, subprocess, sys, time
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from topology.redundant_topology import RedundantTransferTopo
ROOT=pathlib.Path(__file__).resolve().parents[1]
ALLOWED_FAILURE=("s1","s2")
def safe_fail_primary(net):
    """Only permit the declared Mininet switch-to-switch virtual link."""
    if os.geteuid()!=0: raise RuntimeError("D2 requires root; invoke with sudo -n after granting noninteractive access")
    left,right=(net.get(n) for n in ALLOWED_FAILURE); links=net.linksBetween(left,right)
    if len(links)!=1: raise RuntimeError("refusing: expected exactly one Mininet primary link")
    names=(links[0].intf1.name,links[0].intf2.name)
    if any(n=="enp0s1" or not n.startswith(("s1-eth","s2-eth")) for n in names):
        raise RuntimeError("refusing to manipulate a physical or management interface: %r"%(names,))
    net.configLinkStatus(*ALLOWED_FAILURE,"down")
    return names
def terminate(process):
    if process and process.poll() is None:
        process.terminate()
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired: process.kill(); process.wait()
def snapshot(path):
    path.write_text(subprocess.run(["free","-h"],capture_output=True,text=True,timeout=5).stdout + "\n" + subprocess.run(["uptime"],capture_output=True,text=True,timeout=5).stdout)
def main():
    if os.geteuid()!=0: raise SystemExit("Refusing D2: run with sudo -n; interactive sudo is unsafe for automation.")
    evidence=ROOT/"evidence"; evidence.mkdir(exist_ok=True)
    ctl_log=open(evidence/"d2_controller.log","w"); controller=subprocess.Popen([os.environ.get("OSKEN_MANAGER","osken-manager"),str(ROOT/"controller/sdn_controller.py")],stdout=ctl_log,stderr=subprocess.STDOUT)
    net=None; receiver=sender=None
    try:
        snapshot(evidence/"d2_resource_before.txt"); time.sleep(2); net=Mininet(topo=RedundantTransferTopo(),controller=lambda n: RemoteController("c0",ip="127.0.0.1",port=6653),switch=OVSSwitch,link=TCLink,autoSetMacs=True,build=True)
        net.start(); h1,h2=net.get("h1","h2"); h1.setARP("10.0.0.2","00:00:00:00:00:02"); h2.setARP("10.0.0.1","00:00:00:00:00:01")
        src="/tmp/d2_source.bin"; dst="/tmp/d2_received/d2_source.bin"; h1.cmd("dd if=/dev/urandom of=%s bs=1M count=12 status=none"%src); h2.cmd("mkdir -p /tmp/d2_received")
        receiver=h2.popen([sys.executable,str(ROOT/"receiver/udp_receiver.py"),"--host","10.0.0.2","--port","5055","--out","/tmp/d2_received"],stdout=open(ROOT/"evidence/d2_receiver.log","w"),stderr=subprocess.STDOUT)
        time.sleep(.5); sender=h1.popen([sys.executable,str(ROOT/"sender/udp_sender.py"),src,"--host","10.0.0.2","--port","5055"],stdout=open(evidence/"d2_sender.log","w"),stderr=subprocess.STDOUT)
        time.sleep(1); (evidence/"d2_flows_before.txt").write_text(subprocess.run(["ovs-ofctl","-O","OpenFlow13","dump-flows","s1"],capture_output=True,text=True,timeout=10).stdout); interfaces=safe_fail_primary(net); fail_at=time.monotonic()
        sender.wait(timeout=90); receiver.terminate(); receiver.wait(timeout=5)
        a=h1.cmd("sha256sum %s | cut -d' ' -f1"%src).strip(); b=h2.cmd("sha256sum %s | cut -d' ' -f1"%dst).strip(); ok=sender.returncode==0 and a==b
        flows=subprocess.run(["ovs-ofctl","-O","OpenFlow13","dump-flows","s1"],capture_output=True,text=True,timeout=10).stdout
        (evidence/"d2_flows_after.txt").write_text(flows)
        (evidence/"d2_result.txt").write_text("failed_virtual_interfaces=%s\nfailover_trigger_seconds=%.6f\nsource_sha256=%s\ndestination_sha256=%s\nPASS=%s\n"%(interfaces,fail_at,a,b,ok))
        snapshot(evidence/"d2_resource_after.txt"); print("D2 PRACTICAL:","PASS" if ok else "FAIL"); return 0 if ok else 1
    finally:
        terminate(sender); terminate(receiver)
        if net: net.stop()
        terminate(controller); ctl_log.close()
if __name__=='__main__': setLogLevel('info'); raise SystemExit(main())
