# D2 practical

Run `sudo python3 scripts/demo_d2.py` in the prepared Ubuntu Mininet environment. Capture sender/receiver logs and `ovs-ofctl -O OpenFlow13 dump-flows` before and after disabling `s1-s2` or `s2-s4` during an active transfer. Record recovery time, retransmissions, and both SHA-256 values in `evidence/`. This report deliberately has no PASS claim until that run is captured.
