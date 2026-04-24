# ========================
# QuakeComm — simulate.py
# ========================

import random
import math
import time
import json
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
sys.path.append('../backend')

from priority import rank_signals, calculate_priority

# --- Config ---
NUM_USERS        = 1000
NETWORK_LOSS     = 0.60
DELAY_RATE       = 0.20
CORRUPT_RATE     = 0.10
DUPLICATE_RATE   = 0.05
CENTER_LAT       = 37.8
CENTER_LON       = 27.2
RADIUS_DEG       = 0.3

TRUE_STATUS_DIST = {
    "critical": 0.20,
    "trapped":  0.35,
    "safe":     0.45
}

STATUS_LIST = ["critical", "trapped", "safe"]

def weighted_status():
    r = random.random()
    if r < TRUE_STATUS_DIST["critical"]:
        return "critical"
    elif r < TRUE_STATUS_DIST["critical"] + TRUE_STATUS_DIST["trapped"]:
        return "trapped"
    return "safe"

def generate_users(n):
    users = []
    for i in range(n):
        lat = CENTER_LAT + random.uniform(-RADIUS_DEG, RADIUS_DEG)
        lon = CENTER_LON + random.uniform(-RADIUS_DEG, RADIUS_DEG)
        true_status = weighted_status()
        users.append({
            "id": i,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "true_status": true_status,
            "timestamp": int(time.time()) - random.randint(0, 3600)
        })
    return users

def simulate_transmission(users):
    signals = []
    lost = 0
    delayed = 0
    corrupted = 0
    duplicated = 0

    for u in users:
        if random.random() < NETWORK_LOSS:
            lost += 1
            continue

        status = u["true_status"]

        if random.random() < CORRUPT_RATE:
            corrupted += 1
            status = random.choice(STATUS_LIST)

        delay = 0
        if random.random() < DELAY_RATE:
            delayed += 1
            delay = random.randint(30, 300)

        signal = {
            "uuid":        f"sim-{u['id']}-{random.randint(1000,9999)}",
            "timestamp":   u["timestamp"] - delay,
            "lat":         str(u["lat"]),
            "lon":         str(u["lon"]),
            "status":      status,
            "note":        "",
            "received":    int(time.time()),
            "true_status": u["true_status"]
        }

        signals.append(signal)

        if random.random() < DUPLICATE_RATE:
            duplicated += 1
            dup = signal.copy()
            dup["uuid"] = f"dup-{u['id']}"
            signals.append(dup)

    stats = {
        "total_users":   len(users),
        "signals_sent":  len(signals),
        "lost":          lost,
        "delayed":       delayed,
        "corrupted":     corrupted,
        "duplicated":    duplicated,
        "survival_rate": round(len(signals) / len(users), 3)
    }

    return signals, stats

def precision_at_k(ranked_signals, k=10):
    top_k = ranked_signals[:k]
    true_critical_in_top = sum(1 for s in top_k if s.get("true_status") == "critical")
    return round(true_critical_in_top / k, 3)

def recall_at_critical_k(ranked_signals, all_signals, k=10):
    top_k = ranked_signals[:k]
    true_critical_total = sum(1 for s in all_signals if s.get("true_status") == "critical")
    true_critical_in_top = sum(1 for s in top_k if s.get("true_status") == "critical")
    if true_critical_total == 0:
        return 0.0
    return round(true_critical_in_top / true_critical_total, 3)

def time_to_first_hit(ranked_signals):
    for i, s in enumerate(ranked_signals):
        if s.get("true_status") == "critical":
            return i + 1
    return -1

def false_rescue_rate(ranked_signals, k=10):
    top_k = ranked_signals[:k]
    false_rescues = sum(1 for s in top_k if s.get("true_status") == "safe")
    return round(false_rescues / k, 3)

def worst_case_simulation(users):
    signals = []
    for u in users:
        if random.random() < 0.80:
            continue
        signal = {
            "uuid":        f"wc-{u['id']}",
            "timestamp":   u["timestamp"],
            "lat":         str(u["lat"]),
            "lon":         str(u["lon"]),
            "status":      u["true_status"],
            "note":        "",
            "received":    int(time.time()),
            "true_status": u["true_status"]
        }
        signals.append(signal)
    return signals

# --- Plots ---
def plot_transmission(stats):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    labels = ['Lost', 'Delayed', 'Corrupted', 'Duplicated', 'Delivered']
    values = [
        stats['lost'],
        stats['delayed'],
        stats['corrupted'],
        stats['duplicated'],
        stats['signals_sent']
    ]
    colors = ['#ff2020', '#ff8800', '#ffcc00', '#888888', '#00e676']

    bars = ax.bar(labels, values, color=colors, width=0.5)
    ax.set_title('Signal Transmission Stats', color='#efefef', fontsize=13, pad=12)
    ax.set_ylabel('Count', color='#888')
    ax.tick_params(colors='#888')
    for spine in ax.spines.values():
        spine.set_edgecolor('#222')

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                str(val), ha='center', color='#efefef', fontsize=9)

    plt.tight_layout()
    os.makedirs('outputs', exist_ok=True)
    plt.savefig('outputs/transmission_stats.png', dpi=150, facecolor='#0a0a0a')
    plt.close()
    print("[+] Saved: outputs/transmission_stats.png")

def plot_metrics(p_at_k, r_at_k, frr, survival, wc_p_at_k):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    labels = ['Precision@K', 'Recall@K', 'False Rescue\nRate', 'Signal\nSurvival', 'Worst Case\nPrecision@K']
    values = [p_at_k, r_at_k, frr, survival, wc_p_at_k]
    colors = ['#00e676', '#00c853', '#ff2020', '#ff8800', '#888888']

    bars = ax.bar(labels, values, color=colors, width=0.5)
    ax.set_ylim(0, 1.2)
    ax.set_title('System Performance Metrics', color='#efefef', fontsize=13, pad=12)
    ax.set_ylabel('Score (0-1)', color='#888')
    ax.tick_params(colors='#888')
    for spine in ax.spines.values():
        spine.set_edgecolor('#222')

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                str(val), ha='center', color='#efefef', fontsize=9)

    plt.tight_layout()
    plt.savefig('outputs/metrics.png', dpi=150, facecolor='#0a0a0a')
    plt.close()
    print("[+] Saved: outputs/metrics.png")

def plot_signal_map(signals):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    colors = {'critical': '#ff2020', 'trapped': '#ff8800', 'safe': '#00e676'}

    for s in signals:
        c = colors.get(s.get("true_status", "safe"), '#888')
        ax.scatter(float(s["lon"]), float(s["lat"]), c=c, s=8, alpha=0.6)

    patches = [mpatches.Patch(color=c, label=k) for k, c in colors.items()]
    ax.legend(handles=patches, facecolor='#111', labelcolor='#efefef', fontsize=9)
    ax.set_title('Signal Distribution Map', color='#efefef', fontsize=13, pad=12)
    ax.set_xlabel('Longitude', color='#888')
    ax.set_ylabel('Latitude', color='#888')
    ax.tick_params(colors='#888')
    for spine in ax.spines.values():
        spine.set_edgecolor('#222')

    plt.tight_layout()
    plt.savefig('outputs/signal_map.png', dpi=150, facecolor='#0a0a0a')
    plt.close()
    print("[+] Saved: outputs/signal_map.png")

# --- Run ---
def run():
    print("=" * 50)
    print("QuakeComm — Simulation Engine")
    print("=" * 50)

    users = generate_users(NUM_USERS)
    print(f"\n[+] Generated {NUM_USERS} users")

    signals, stats = simulate_transmission(users)
    print(f"\n[+] Transmission stats:")
    for k, v in stats.items():
        print(f"    {k}: {v}")

    ranked = rank_signals(signals)

    p_at_k  = precision_at_k(ranked, k=10)
    r_at_k  = recall_at_critical_k(ranked, signals, k=10)
    t_first = time_to_first_hit(ranked)
    frr     = false_rescue_rate(ranked, k=10)

    print(f"\n[+] Metrics (K=10):")
    print(f"    Precision@K:       {p_at_k}")
    print(f"    Recall@critical-K: {r_at_k}")
    print(f"    Time-to-first-hit: #{t_first}")
    print(f"    False rescue rate: {frr}")
    print(f"    Signal survival:   {stats['survival_rate']}")

    wc_signals = worst_case_simulation(users)
    wc_ranked  = rank_signals(wc_signals)
    wc_p_at_k  = precision_at_k(wc_ranked, k=10)

    print(f"\n[+] Worst case (80% network collapse):")
    print(f"    Signals survived:  {len(wc_signals)}/{NUM_USERS}")
    print(f"    Precision@K:       {wc_p_at_k}")

    # Plots
    print("\n[+] Generating plots...")
    plot_transmission(stats)
    plot_metrics(p_at_k, r_at_k, frr, stats['survival_rate'], wc_p_at_k)
    plot_signal_map(signals)

    print("\n" + "=" * 50)
    print("Simulation complete.")
    print("=" * 50)

if __name__ == "__main__":
    run()