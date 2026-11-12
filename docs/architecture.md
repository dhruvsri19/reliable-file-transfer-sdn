# Architecture

The sender divides a file into chunks and numbers each `DATA` packet from zero. The receiver stores packets keyed by sequence number, ACKs every data packet, ignores a duplicate while still ACKing it, and requests every missing index after `END`. Sender timeouts cause bounded retransmission. The receiver combines packets in sequence order and compares its SHA-256 digest and reconstructed byte count to metadata before sending `DONE`.

The topology exposes two switch paths. The controller speaks OpenFlow 1.3 and installs learned unicast forwarding entries. D2 verification must demonstrate traffic changing from the `s2` branch to the `s3` branch following a real link-state failure, without restarting sender or receiver.
