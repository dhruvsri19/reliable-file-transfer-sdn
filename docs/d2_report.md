# D2 practical

The verified Ubuntu run transferred 128 MiB in 9.07 s. During the same session, Mininet disabled only virtual link `s1-s2`; the controller logged backup activation and the `s1` post-failover flow sent 180,401 packets to port 3 (the `s3` branch). Sender logged one timeout/retransmission and both endpoints produced SHA-256 `d916e1e0212d6d8a16432611f427b74b8fef71885a34eb9be85c48f4bcff882c`. See `evidence/d2_result.txt` and the before/after flow dumps.
