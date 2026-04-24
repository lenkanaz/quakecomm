# ========================
# QuakeComm — priority.py
# ========================

import time
import math

# --- Weights ---
W1 = 0.40  # status
W2 = 0.25  # time decay
W3 = 0.20  # isolation
W4 = 0.10  # cluster risk
W5 = 0.05  # redundancy

# --- Status Scores ---
STATUS_SCORES = {
    "critical": 100,
    "trapped":  70,
    "safe":     10
}

# --- Min-Max Normalization ---
def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

# --- Time Decay ---
def time_decay_score(timestamp: int) -> float:
    now = int(time.time())
    if timestamp > 1e10:
        timestamp = timestamp / 1000
    age_seconds = now - timestamp
    if age_seconds < 0:
        age_seconds = 0
    decay = math.exp(-age_seconds / 86400)
    return decay

# --- Haversine Distance (km) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- Isolation Score ---
def isolation_score(lat: float, lon: float, all_signals: list, radius_km: float = 0.5) -> float:
    nearby = 0
    for s in all_signals:
        try:
            other_lat = float(s["lat"])
            other_lon = float(s["lon"])
            dist = haversine(lat, lon, other_lat, other_lon)
            if dist < radius_km:
                nearby += 1
        except:
            continue
    if nearby <= 1:
        return 1.0
    return max(0.0, 1.0 - (nearby / 10))

# --- Cluster Risk ---
def cluster_risk_score(lat: float, lon: float, all_signals: list, radius_km: float = 0.5) -> float:
    nearby = 0
    for s in all_signals:
        try:
            other_lat = float(s["lat"])
            other_lon = float(s["lon"])
            dist = haversine(lat, lon, other_lat, other_lon)
            if dist < radius_km:
                nearby += 1
        except:
            continue
    return min(1.0, nearby / 10)

# --- Redundancy Score ---
def redundancy_score(uuid: str, all_signals: list) -> float:
    count = sum(1 for s in all_signals if s.get("uuid") == uuid)
    return min(1.0, count / 3)

# --- Main Priority Calculator ---
def calculate_priority(signal: dict, all_signals: list) -> float:
    try:
        lat = float(signal["lat"])
        lon = float(signal["lon"])
    except:
        lat, lon = 0.0, 0.0

    s1 = normalize(STATUS_SCORES.get(signal["status"], 0), 0, 100)
    s2 = time_decay_score(signal["timestamp"])
    s3 = isolation_score(lat, lon, all_signals)
    s4 = cluster_risk_score(lat, lon, all_signals)
    s5 = redundancy_score(signal["uuid"], all_signals)

    score = (W1 * s1) + (W2 * s2) + (W3 * s3) + (W4 * s4) + (W5 * s5)

    return round(score, 4)

# --- Rank All Signals ---
def rank_signals(all_signals: list) -> list:
    scored = []
    for s in all_signals:
        priority = calculate_priority(s, all_signals)
        scored.append({**s, "priority_score": priority})
    return sorted(scored, key=lambda x: x["priority_score"], reverse=True)