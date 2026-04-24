# ========================
# QuakeComm — parser.py
# ========================

import time

def generate_checksum(text: str) -> str:
    hash_val = 0
    for ch in text:
        hash_val = ((hash_val << 5) - hash_val) + ord(ch)
        hash_val &= 0xFFFFFFFF
    return hex(abs(hash_val))[2:8].upper()

def parse_packet(raw: str) -> dict | None:
    try:
        parts = raw.strip().split("|")
        
        # Format: QK|uuid|timestamp|lat|lon|status|note|checksum
        if len(parts) < 7:
            return None
        
        prefix    = parts[0]
        uuid      = parts[1]
        timestamp = parts[2]
        lat       = parts[3]
        lon       = parts[4]
        status    = parts[5]
        note      = parts[6] if len(parts) > 6 else ""
        checksum  = parts[7] if len(parts) > 7 else ""
        
        # Prefix kontrolü
        if prefix != "QK":
            return None
        
        # Status kontrolü
        if status not in ["critical", "trapped", "safe"]:
            return None
        
        # Checksum doğrulama
        core = f"QK|{uuid}|{timestamp}|{lat}|{lon}|{status}|{note}"
        expected = generate_checksum(core)
        if checksum and checksum != expected:
            return None
        
        return {
            "uuid":      uuid,
            "timestamp": int(timestamp),
            "lat":       lat,
            "lon":       lon,
            "status":    status,
            "note":      note,
            "received":  int(time.time())
        }
    
    except Exception:
        return None