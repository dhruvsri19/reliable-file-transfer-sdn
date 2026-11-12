# Performance analysis

Run each scenario three times: normal, controlled loss, increased delay, and primary-path failure. Record file size, elapsed time, goodput (`bytes * 8 / seconds`), retransmissions, duplicate count, SHA-256 outcome, and—for failover—link-down to first successful backup-path packet time. Store raw terminal logs and CSV output in `evidence/`; generate graphs only from those recorded values.
