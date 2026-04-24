# System Architecture

## Overview

QuakeComm is a three-layer system designed to operate under network failure conditions.

User (PWA) → Transport Layer (SMS/HTTP) → Backend → Admin Panel

---

## Layer 1 — Client (PWA)

Files: client/index.html, client/app.js, client/sw.js

- Single-screen interface operable in under 10 seconds
- Three operating modes:
  - Full Mode: internet available, direct HTTP POST
  - Degraded Mode: no internet, SMS queue via Twilio
  - Dead Mode: no connectivity, local storage queue, retry on reconnect
- Service worker enables offline operation after first load
- GPS acquired automatically, fallback to UNKNOWN if unavailable

Message format: QK|uuid|timestamp|lat|lon|status|note|checksum

---

## Layer 2 — Backend (Python/FastAPI)

Files: backend/main.py, backend/parser.py, backend/priority.py, backend/conflict.py, backend/db.py

### Parse Engine
- Validates message format and checksum
- Rejects malformed packets
- Accepts partial packets with reduced confidence

### Event Buffer
- 5-second window collects incoming messages
- Reorders by timestamp before processing
- Handles out-of-order SMS delivery

### UUID Deduplication
- Duplicate messages silently discarded
- Prevents double-counting of retransmissions

### Conflict Resolution
- Detects conflicting signals within 100m radius
- Weighted voting with recency bias
- Outputs certainty vs uncertainty classification

### Priority Engine
priority = w1 x status + w2 x time_decay + w3 x isolation + w4 x cluster_risk + w5 x redundancy

- All features min-max normalized (0-1)
- Weights calibrated via simulation loop
- Adaptive isolation radius based on signal density

---

## Layer 3 — Admin Panel

Files: client/admin.html, client/admin.js, client/admin.css

- Leaflet.js map with OpenStreetMap tiles
- Certainty Map: reliable, non-conflicting signals
- Uncertainty Map: conflicting signals flagged for review
- Priority list sorted by score, top 10 first
- Google Maps navigation link per signal
- 5 language support: EN, TR, DE, EL, IT
- Auto-refresh every 30 seconds

---

## Simulation

Files: simulation/simulate.py

- Generates 1000 synthetic users around a disaster zone
- Injects realistic noise: 60% loss, 20% delay, 10% corruption, 5% duplication
- Evaluates priority engine performance
- Outputs: Precision@K, Recall@critical-K, Time-to-first-hit, False rescue rate
- Worst-case scenario: 80% network collapse

---

## Data Flow

1. User opens PWA, selects status, GPS acquired
2. Message packet built: QK|uuid|ts|lat|lon|status|note|checksum
3. Sent via HTTP or SMS/Twilio
4. Backend receives, parses, validates, buffers
5. Buffer flushes every 5s, dedup, conflict check, priority score
6. Stored in database
7. Admin panel fetches /api/signals, ranked by priority
8. Rescue team dispatched to highest-score locations