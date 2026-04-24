# System Tradeoffs

Design decisions made in QuakeComm, and the reasoning behind each.

---

## Why SMS?

SMS works on GSM networks without internet.
During the 2023 Kahramanmaraş earthquake, internet collapsed but GSM partially survived.
SMS requires no special hardware — every phone has it.

**Rejected alternatives:**
- WhatsApp / Telegram → requires internet
- Push notifications → requires internet
- Email → requires internet

## Why Not LoRa?

LoRa is a low-power radio protocol with excellent range and no GSM dependency.
It would be ideal — but requires dedicated hardware (LoRa modules, gateways).
In a disaster, nobody carries LoRa hardware.

QuakeComm is designed for existing infrastructure, not new hardware.
LoRa integration is noted as future work.

## Why Not Bluetooth Mesh?

Bluetooth mesh could relay messages device-to-device without any infrastructure.
This is theoretically powerful but adds significant complexity:
- Requires all devices to have the app running in background
- Battery drain
- Range limited to ~10m per hop

Noted as future work for Layer 6 fallback.

## Why PWA Instead of Native App?

A native app requires App Store / Play Store installation.
During a disaster, nobody downloads a new app.
PWA installs silently when the user first visits the site.
Works offline after first load via service worker.

Tradeoff: user must have visited the site before the disaster.
This is documented as a limitation.

## Why Heuristic Labels in Simulation?

Human-annotated ground truth would require real disaster data.
This does not exist publicly at the required scale.
Heuristic simulation is the standard approach for disaster system evaluation.
Labels are documented as synthetic — results should be interpreted accordingly.

## Why In-Memory Database (MVP)?

PostgreSQL integration is architecturally included but not fully deployed in MVP.
In-memory storage was chosen for development speed.
Production deployment requires persistent storage — noted as next step.