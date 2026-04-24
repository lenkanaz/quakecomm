# System Assumptions

QuakeComm is designed under the following assumptions about the environment it operates in.
These are not bugs or oversights — they are deliberate acknowledgements of real-world constraints.

---

## Network

- SMS delivery is not guaranteed. Messages may be lost, delayed, duplicated, or arrive out of order.
- Internet connectivity cannot be assumed during a disaster. The system is designed to function without it.
- GSM towers may partially or fully collapse. Signal survival rate drops proportionally.
- Cluster-based failures are expected: devices in the same area will fail together, not independently.

## Location

- GPS coordinates may be unavailable indoors or under rubble.
- If GPS is unavailable, the message is still accepted with reduced location confidence.
- Coordinate accuracy varies by device and environment.

## Data

- Messages are treated as signals, not ground truth.
- The system does not assume any message is fully accurate.
- Duplicate messages are expected and handled via UUID deduplication.
- Corrupted messages are rejected at the parse layer.

## Users

- Users may be in panic. The interface must be operable in under 10 seconds.
- Users may send incorrect status (e.g. a bystander marking someone else as critical).
- Not all affected people will have a charged phone or access to the app.

## Labels

- Simulation ground truth labels are heuristic-based, not human-annotated.
- Model evaluation is relative to simulated truth, not real-world outcomes.
- This is documented as a limitation, not hidden.