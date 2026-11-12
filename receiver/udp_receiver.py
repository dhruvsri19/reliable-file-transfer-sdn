import argparse, base64, hashlib, json, os, socket

def enc(x): return json.dumps(x, separators=(",", ":")).encode()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5005)
    ap.add_argument("--out", default="received_files")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((a.host, a.port))
    print(f"[receiver] Listening on {a.host}:{a.port}")
    meta, chunks = None, {}
    while True:
        raw, peer = s.recvfrom(65535)
        try: p = json.loads(raw.decode())
        except Exception: continue
        if p.get("type") == "START":
            meta = p
            chunks = {}
            s.sendto(enc({"type":"ACK_START"}), peer)
            print(f"[receiver] Started {os.path.basename(meta['name'])}: {meta['size']} bytes, {meta['total']} packets")
        elif p.get("type") == "DATA" and meta:
            n = int(p["seq"])
            if n not in chunks:
                chunks[n] = base64.b64decode(p["data"])
                print(f"[receiver] Packet {n+1}/{meta['total']} received")
            else:
                print(f"[receiver] Duplicate packet {n} ignored")
            s.sendto(enc({"type":"ACK","seq":n}), peer)
        elif p.get("type") == "END" and meta:
            missing = [i for i in range(int(meta["total"])) if i not in chunks]
            if missing:
                s.sendto(enc({"type":"MISSING","seqs":missing}), peer)
                continue
            data = b"".join(chunks[i] for i in range(int(meta["total"])))
            digest = hashlib.sha256(data).hexdigest()
            path = os.path.join(a.out, os.path.basename(meta["name"]))
            with open(path, "wb") as f: f.write(data)
            ok = len(data) == int(meta["size"]) and digest == meta["sha256"]
            s.sendto(enc({"type":"DONE","ok":ok,"size":len(data),"sha256":digest,"path":path}), peer)
            print(f"[receiver] Saved: {os.path.abspath(path)}")
            print(f"[receiver] SHA-256: {digest}")
            print(f"[receiver] Integrity check: {'PASS' if ok else 'FAIL'}")
            meta, chunks = None, {}
if __name__ == "__main__": main()
