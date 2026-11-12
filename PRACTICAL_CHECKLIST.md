# Classroom Practical Checklist — November 13

## Before class

- [ ] Start Ubuntu and confirm: `ssh -o BatchMode=yes -i ~/.ssh/id_ed25519 dhruv@<VM_IP>`.
- [ ] Work in `/home/dhruv/reliable-file-transfer-sdn`; do not touch Network Monitoring.
- [ ] Do not run `mn -c` while D2 is active.

## D1

```bash
cd /home/dhruv/reliable-file-transfer-sdn
python3 scripts/demo_d1.py
```

Show the forced loss at sequence 4, retransmission, SHA-256 integrity PASS, and `D1 PRACTICAL: PASS`.

## D2

```bash
cd /home/dhruv/reliable-file-transfer-sdn
OSKEN_PYTHON=/home/dhruv/network-monitoring-sdn/.venv/bin/python \
PYTHONPATH=/home/dhruv/reliable-file-transfer-sdn \
.venv/bin/python scripts/run_d2_authorized.py
```

The launcher uses only approved `sudo -n /usr/bin/mn` and `sudo -n /usr/bin/ovs-ofctl`; it disables only virtual link `s1-s2`, never `enp0s1`, VM addressing, routes, or SSH.

After it ends, show:

```bash
cat evidence/d2_result.txt
cat evidence/d2_controller.log
cat evidence/d2_flows_before.txt
cat evidence/d2_flows_after.txt
tail -n 12 evidence/d2_sender.log
tail -n 12 evidence/d2_receiver.log
```

Expected proof: `D2 PRACTICAL: PASS`, matching hashes, controller text `PRIMARY LINK FAILURE: activating s3 backup`, and post-failover `s1` action `output:3`.

## If a run fails

Do not claim PASS. Keep the evidence logs, confirm the VM IP and `sudo -n /usr/bin/mn --version`, then diagnose before retrying.
