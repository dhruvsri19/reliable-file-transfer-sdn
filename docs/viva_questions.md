# Viva questions

**Why UDP?** It exposes reliability mechanisms at the application layer.

**Why sequence numbers?** They identify ordering, loss, and duplicates.

**Why SHA-256?** ACKs show delivery, whereas the digest validates complete reconstructed content.

**What happens during loss?** The sender's ACK timeout retransmits up to the configured bound.

**What proves SDN rerouting?** Link failure evidence plus OpenFlow flow-table and traffic-path evidence while the same transfer continues.
