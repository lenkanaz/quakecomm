# ========================
# QuakeComm — conflict.py
# ========================

import time
from priority import haversine

CONFLICT_RADIUS_KM = 0.1  # 100 metre
RECENCY_WINDOW = 300       # 5 dakika

def find_conflicts(all_signals: list) -> list:
    """
    Aynı bölgeden çelişkili sinyalleri tespit et.
    """
    conflicts = []
    checked = set()

    for i, s1 in enumerate(all_signals):
        for j, s2 in enumerate(all_signals):
            if i >= j:
                continue
            if (i, j) in checked:
                continue
            checked.add((i, j))

            try:
                lat1, lon1 = float(s1["lat"]), float(s1["lon"])
                lat2, lon2 = float(s2["lat"]), float(s2["lon"])
            except:
                continue

            dist = haversine(lat1, lon1, lat2, lon2)

            if dist < CONFLICT_RADIUS_KM and s1["status"] != s2["status"]:
                conflicts.append({
                    "signal_1": s1["uuid"],
                    "signal_2": s2["uuid"],
                    "distance_km": round(dist, 4),
                    "status_1": s1["status"],
                    "status_2": s2["status"],
                    "location": {"lat": lat1, "lon": lon1}
                })

    return conflicts

def resolve_conflict(signals_in_zone: list) -> dict:
    """
    Aynı bölgedeki çelişkili sinyaller için ağırlıklı oylama.
    Recency bias: yeni sinyal daha güvenilir.
    """
    now = int(time.time())

    STATUS_WEIGHT = {
        "critical": 3,
        "trapped":  2,
        "safe":     1
    }

    scores = {"critical": 0.0, "trapped": 0.0, "safe": 0.0}

    for s in signals_in_zone:
        ts = s["timestamp"]
        if ts > 1e10:
            ts = ts / 1000

        age = now - ts
        recency_weight = max(0.1, 1.0 - (age / RECENCY_WINDOW))
        status_weight = STATUS_WEIGHT.get(s["status"], 1)

        scores[s["status"]] += status_weight * recency_weight

    resolved_status = max(scores, key=scores.get)

    return {
        "resolved_status": resolved_status,
        "scores": {k: round(v, 4) for k, v in scores.items()},
        "signal_count": len(signals_in_zone)
    }