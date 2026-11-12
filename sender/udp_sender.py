import argparse, base64, hashlib, json, os, socket, time
CHUNK = 700
TIMEOUT = 0.8
RETRIES = 8
def enc(x): return json.dumps(x, separators=(",", ":")).encode()
def recv(s, timeout=TIMEOUT):
    s.settimeout(timeout)
    raw, _ = s.recvfrom(65535)
    return json.loads(raw.decode())
def send_wait(s, addr, packet, want, seq=None):
    for attempt in range(1, RETRIES + 1):
        s.sendto(enc(packet), addr)
        try:
            r = recv(s)
            if r.get("type") == want and (seq is None or r.get("seq") == seq): return r
        except socket.timeout: pass
        print(f"[sender] Timeout; retry {attempt}/{RETRIES}")
    raise TimeoutError("No acknowledgement received")
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5005)
    ap.add_argument("--drop-first", type=int, default=-1, help="simulate loss for this zero-based packet index")
    ap.add_argument("--chunk-size", type=int, default=CHUNK)
    a = ap.parse_args()
    with open(a.file, "rb") as f: data = f.read()
    if not 1 <= a.chunk_size <= 45000: raise SystemExit("--chunk-size must be 1..45000")
    chunks = [data[i:i+a.chunk_size] for i in range(0, len(data), a.chunk_size)] or [b""]
    digest = hashlib.sha256(data).hexdigest()
    addr = (a.host, a.port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[sender] Sending {os.path.basename(a.file)} ({len(data)} bytes)")
    print(f"[sender] SHA-256: {digest}")
    start = time.time()
    send_wait(s, addr, {"type":"START","name":os.path.basename(a.file),"total":len(chunks),"size":len(data),"sha256":digest}, "ACK_START")
    simulated = False
    for i, chunk in enumerate(chunks):
        pkt = {"type":"DATA","seq":i,"data":base64.b64encode(chunk).decode()}
        if i == a.drop_first and not simulated:
            simulated = True
            print(f"[sender] DEMO: simulating loss of packet {i}; waiting for timeout")
            time.sleep(TIMEOUT + 0.15)
            print(f"[sender] Retransmitting packet {i}")
        send_wait(s, addr, pkt, "ACK", i)
    result = None
    for _ in range(RETRIES):
        s.sendto(enc({"type":"END"}), addr)
        try:
            r = recv(s)
            if r.get("type") == "DONE":
                result = r
                break
            if r.get("type") == "MISSING":
                for i in r["seqs"]:
                    pkt = {"type":"DATA","seq":i,"data":base64.b64encode(chunks[i]).decode()}
                    send_wait(s, addr, pkt, "ACK", i)
        except socket.timeout: print("[sender] Waiting for final confirmation...")
    s.close()
    if not result: raise TimeoutError("No final confirmation")
    print(f"[sender] Integrity check: {'PASS' if result['ok'] else 'FAIL'}")
    print(f"[sender] Total time: {time.time()-start:.2f} seconds")
    print(f"[sender] Receiver saved file at: {result['path']}")
    if not result["ok"]: raise SystemExit("Integrity check failed")
if __name__ == "__main__": main()
