# Failure Modes

This document describes how QuakeComm behaves under various failure conditions.
The system is designed to degrade gracefully — not crash.

---

## Level 0 — Full System
All components operational. Internet available, GPS acquired, backend running.
→ Normal operation.

## Level 1 — Internet Lost
SMS fallback activates. Messages queued locally and sent when connectivity returns.
→ Degraded mode. Delayed delivery, no data loss.

## Level 2 — GSM Partially Down
Some messages lost. Event buffer + UUID deduplication handles partial delivery.
→ Reduced signal count. Priority engine still functional on received signals.

## Level 3 — GPS Unavailable
Message accepted without coordinates. Location confidence marked as low.
→ Signal appears on map at last known location or excluded from map view.

## Level 4 — Backend Offline
Messages stored in local queue. On recovery, queue flushes automatically.
UUID deduplication prevents duplicate entries after reconnection.
→ No data loss. Priority recalculated after flush.

## Level 5 — 80% Network Collapse
Simulation shows 193/1000 signals survive.
Precision@K remains 1.0 — system still correctly prioritizes with limited data.
→ Reduced coverage but accurate prioritization.

---

## Failure That Cannot Be Solved in Software

Signal survival rate is fundamentally limited by physical infrastructure.
If all GSM towers and internet are down, no signal can be transmitted.
This is a hardware/infrastructure problem, not a software problem.

Future work: device-to-device mesh forwarding as a Layer 6 fallback.