#!/usr/bin/env python3
"""Self-contained D1 practical: binary UDP transfer with a forced retransmission."""
from __future__ import annotations
import hashlib, os, pathlib, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rft-d1-") as td:
        temp = pathlib.Path(td); source = temp / "d1_binary.bin"; output = temp / "received"
        source.write_bytes(os.urandom(256 * 1024 + 37))
        receiver = subprocess.Popen([sys.executable, str(ROOT / "receiver/udp_receiver.py"), "--port", "5055", "--out", str(output)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            time.sleep(.25)
            sender = subprocess.run([sys.executable, str(ROOT / "sender/udp_sender.py"), str(source), "--port", "5055", "--drop-first", "4"], text=True, capture_output=True, timeout=45)
            received = output / source.name
            valid = sender.returncode == 0 and received.exists() and hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(received.read_bytes()).digest()
            print(sender.stdout, end=""); print(sender.stderr, end="", file=sys.stderr); print("D1 PRACTICAL:", "PASS" if valid else "FAIL")
            return 0 if valid else 1
        finally:
            receiver.terminate(); receiver.wait(timeout=5)
if __name__ == "__main__": raise SystemExit(main())
