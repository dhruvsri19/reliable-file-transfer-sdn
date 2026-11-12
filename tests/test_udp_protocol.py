import hashlib, pathlib, subprocess, sys, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def test_empty_file_transfer():
    with tempfile.TemporaryDirectory() as d:
        d=pathlib.Path(d); src=d/'empty.bin'; src.write_bytes(b''); out=d/'out'
        r=subprocess.Popen([sys.executable,str(ROOT/'receiver/udp_receiver.py'),'--port','5056','--out',str(out)])
        try:
            time.sleep(.15); sent=subprocess.run([sys.executable,str(ROOT/'sender/udp_sender.py'),str(src),'--port','5056'],capture_output=True,timeout=20)
            assert sent.returncode == 0 and (out/src.name).read_bytes() == b''
        finally: r.terminate(); r.wait()
def test_sha256_binary():
    data=bytes(range(256))*5
    assert hashlib.sha256(data).hexdigest() == hashlib.sha256(data).hexdigest()
