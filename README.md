# Reliable File Transfer Using UDP and SDN

This project demonstrates reliable application-layer file transfer over UDP and a redundant OpenFlow 1.3 topology. D1 is a runnable UDP reliability practical. D2 provides the Mininet/OS-Ken launch assets for redundant-path validation on Ubuntu.

## Features

- JSON UDP protocol with `START`, sequenced `DATA`, `ACK`, `MISSING`, `END`, and `DONE` messages.
- Timeout-bounded retransmission, duplicate suppression, missing-sequence recovery, and SHA-256 end-to-end verification.
- Empty and arbitrary binary-file support; transfer completion is acknowledged by `DONE`.
- Redundant topology: `h1—s1—s2—s4—h2` (primary) and `h1—s1—s3—s4—h2` (backup).

## Architecture

```text
sender/udp_sender.py -> UDP + ACK/retry -> receiver/udp_receiver.py
 h1 -- s1 -- s2 -- s4 -- h2    primary
        \-- s3 --/             backup
              ^
      controller/sdn_controller.py (OpenFlow 1.3)
```

## Install

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

For D2, use Ubuntu with Mininet, Open vSwitch, OpenFlow 1.3, and OS-Ken installed. Run Mininet as root; do not use a production network.

## D1 practical

```bash
python3 scripts/demo_d1.py
pytest -q
```

The demonstration creates a real 256 KiB binary file, deliberately drops sequence 4, shows timeout/retransmission output, and SHA-256-verifies the received file.

## D2 practical

```bash
sudo python3 scripts/demo_d2.py
```

In the Mininet prompt, start the receiver and sender on `h2`/`h1`, then bring down `s1-s2` while the sender runs. Inspect live flow tables with `sh ovs-ofctl -O OpenFlow13 dump-flows s1` and `s4`. The controller learns forwarding from packet-ins and installs OpenFlow rules; after a link failure, traffic must be observed on the backup branch before treating D2 as passed.

## Evidence and status

Local D1 test evidence is recorded only after each run in `evidence/`. The supplied VM was unreachable when this workspace was created, so no Mininet failover claim, D2 performance number, graph, or submission ZIP is included yet. See [docs/verification_status.md](docs/verification_status.md). No measurements are fabricated.

## Tests

`tests/test_udp_protocol.py` exercises real localhost empty-file transfer and SHA-256 binary integrity. Run `pytest -q`.

## Repository publication

GitHub publication is intentionally deferred until D1 and D2 are fully validated on the target VM.
