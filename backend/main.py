# ========================
# QuakeComm — main.py
# ========================

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from parser import parse_packet
from db import save_signal, is_duplicate, get_all_signals
from priority import rank_signals
from conflict import find_conflicts, resolve_conflict
import uvicorn
import asyncio
from collections import deque

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Event Buffer ---
BUFFER_WINDOW = 5
event_buffer = deque()
buffer_lock = asyncio.Lock()

async def flush_buffer():
    while True:
        await asyncio.sleep(BUFFER_WINDOW)
        async with buffer_lock:
            if not event_buffer:
                continue
            sorted_events = sorted(event_buffer, key=lambda x: x["timestamp"])
            event_buffer.clear()
            for parsed in sorted_events:
                if is_duplicate(parsed["uuid"]):
                    print(f"[DEDUP] Duplicate skipped: {parsed['uuid']}")
                    continue
                save_signal(parsed)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(flush_buffer())

@app.get("/")
def root():
    return {"status": "QuakeComm backend running"}

@app.post("/api/signal")
async def receive_signal(request: Request):
    body = await request.json()
    packet = body.get("packet", "")
    parsed = parse_packet(packet)
    if not parsed:
        return {"status": "error", "message": "Invalid packet"}
    async with buffer_lock:
        event_buffer.append(parsed)
    return {"status": "queued", "uuid": parsed["uuid"]}

@app.get("/api/signals")
def get_signals():
    all_signals = get_all_signals()
    ranked = rank_signals(all_signals)
    return {"signals": ranked}

@app.get("/api/signals/top")
def get_top_signals(k: int = 10):
    all_signals = get_all_signals()
    ranked = rank_signals(all_signals)
    return {"signals": ranked[:k]}

@app.get("/api/conflicts")
def get_conflicts():
    all_signals = get_all_signals()
    conflicts = find_conflicts(all_signals)
    return {"conflicts": conflicts, "count": len(conflicts)}

@app.get("/api/conflicts/resolve")
def resolve_conflicts():
    all_signals = get_all_signals()
    conflicts = find_conflicts(all_signals)
    if not conflicts:
        return {"message": "No conflicts found"}
    result = resolve_conflict(all_signals)
    return {"resolution": result}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)