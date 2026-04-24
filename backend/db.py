# ========================
# QuakeComm — db.py
# ========================

signals = []
seen_uuids = set()

def is_duplicate(uuid: str) -> bool:
    return uuid in seen_uuids

def save_signal(parsed: dict):
    seen_uuids.add(parsed["uuid"])
    signals.append(parsed)
    print(f"[DB] Signal saved: {parsed['uuid']} | {parsed['status']} | {parsed['lat']},{parsed['lon']}")

def get_all_signals():
    return signals

def get_signals_by_status(status: str):
    return [s for s in signals if s["status"] == status]