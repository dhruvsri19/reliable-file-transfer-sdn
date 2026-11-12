# Demo guide

1. Run the D1 launcher and show forced loss, retransmission, and digest PASS.
2. Start OS-Ken and the redundant Mininet topology using the D2 launcher.
3. Start receiver on h2 and send a sufficiently large file from h1.
4. Dump switch flows, disable a primary link during the transfer, and dump flows again.
5. Show the unchanged transfer session, completion, source/destination digests, and recovery timing.
