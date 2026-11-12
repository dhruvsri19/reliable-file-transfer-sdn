# Dynamic SDN Failover for Reliable UDP File Transfer (D2)

This D2-only submission demonstrates a reliable UDP file-transfer session that survives a live SDN primary-link failure without restarting sender or receiver.

## Architecture

```text
 h1 -- s1 -- s2 -- s4 -- h2   primary
        \-- s3 --/            backup
              ^
      OS-Ken OpenFlow 1.3 controller
```

The controller installs primary forwarding. On virtual Mininet link `s1-s2` failure, its OpenFlow port-status event activates the `s3` backup rule. UDP reliability remains application-layer: sequence numbers, ACKs, bounded timeout retransmission, duplicate suppression, missing-packet recovery, and SHA-256 verification.

## Requirements

- Ubuntu, Python 3.12, Mininet 2.3, Open vSwitch/OpenFlow 1.3, OS-Ken 4.2.2.
- Passwordless access only to `/usr/bin/mn` and `/usr/bin/ovs-ofctl`; privileged Python is not required.

## Verified D2 practical

```bash
cd /home/dhruv/reliable-file-transfer-sdn
OSKEN_PYTHON=/home/dhruv/network-monitoring-sdn/.venv/bin/python \
PYTHONPATH=/home/dhruv/reliable-file-transfer-sdn \
.venv/bin/python scripts/run_d2_authorized.py
```

The launcher creates the redundant topology, starts one 128 MiB UDP session, disables only virtual link `s1-s2`, captures before/after flows, and checks endpoint hashes. It never changes physical interfaces, management IPs, routes, or SSH.

## Verified results

- 128 MiB completed in 9.07 seconds during the same session.
- `s1-s2` failed and the controller activated backup `s3`.
- One retransmission occurred.
- Matching SHA-256: `d916e1e0212d6d8a16432611f427b74b8fef71885a34eb9be85c48f4bcff882c`.
- Post-failover OpenFlow rule used `actions=output:3` for 180,401 packets.

See `evidence/d2_result.txt`, `evidence/d2_controller.log`, and the before/after flow dumps.
