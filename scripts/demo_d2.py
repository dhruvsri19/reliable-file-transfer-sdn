#!/usr/bin/env python3
"""D2 launcher (run as root on Ubuntu with Mininet + OS-Ken installed)."""
import pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    controller=subprocess.Popen(["osken-manager",str(ROOT/"controller/sdn_controller.py")])
    try:
        return subprocess.call(["sudo","mn","--custom",str(ROOT/"topology/redundant_topology.py"),"--topo","redundanttransfer","--controller","remote,ip=127.0.0.1,port=6653","--switch","ovs,protocols=OpenFlow13"])
    finally: controller.terminate(); controller.wait()
if __name__ == '__main__': raise SystemExit(main())
