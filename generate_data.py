#!/usr/bin/env python3
"""
Genera una cartera B2B SINTÉTICA para demostrar el motor de Customer Health Score.

100% datos ficticios: ninguna empresa, monto ni persona es real.
Generates a SYNTHETIC B2B portfolio to demo the Customer Health Score engine.
100% fictional data: no real company, amount or person.

Uso / Usage:
    python generate_data.py [--seed 42] [--accounts 60]
"""
import argparse
import datetime
import json
import random

# ---------------------------------------------------------------------------
# Vocabulario ficticio / fictional vocabulary
# ---------------------------------------------------------------------------
NAME_A = [
    "Northwind", "Vertex", "BlueOak", "Cinder", "Atlas", "Brightside",
    "Cobalt", "Delta", "Everest", "Fjord", "Granite", "Halcyon",
    "Ironwood", "Juniper", "Keystone", "Larkspur", "Meridian", "Nimbus",
    "Oakleaf", "Pinnacle", "Quarry", "Redwood", "Summit", "Tidal",
    "Umbra", "Vantage", "Willow", "Zenith", "Aster", "Boulder",
]
NAME_B = [
    "Logistics", "Analytics", "Capital", "Health", "Retail Group", "Systems",
    "Media", "Manufacturing", "Cloud", "Ventures", "Energy", "Foods",
    "Insurance", "Labs", "Networks", "Payments", "Robotics", "Software",
    "Telecom", "Warehousing",
]
INDUSTRIES = ["Fintech", "Healthcare", "Retail", "Logistics", "SaaS",
              "Manufacturing", "Media & Comms"]
REGIONS = ["North America", "LATAM", "EMEA", "APAC"]

# ARR (USD) por tier / by tier
TIER_ARR = {
    "Strategic": (200_000, 800_000),
    "Enterprise": (50_000, 199_000),
    "Growth": (10_000, 49_000),
    "SMB": (2_000, 9_000),
}

# Arquetipos: determinan el perfil de señales / archetypes shape the signals
ARCHETYPES = ["healthy", "watch", "at_risk", "critical", "expansion", "churned"]
ARCHETYPE_WEIGHTS = [0.40, 0.25, 0.15, 0.08, 0.07, 0.05]


def _pick_tier(rng):
    return rng.choices(
        ["Strategic", "Enterprise", "Growth", "SMB"], weights=[0.08, 0.22, 0.40, 0.30]
    )[0]


def _tier_seats(tier):
    return {"Strategic": (150, 600), "Enterprise": (60, 200),
            "Growth": (10, 80), "SMB": (2, 15)}[tier]


def _profile_for(arch, rng):
    """Devuelve señales coherentes con el arquetipo / returns archetype-consistent signals."""
    p = {
        "healthy":   dict(adopt=(0.75, 1.00), engage=(70, 100), support=(85, 100),
                          nps=(8, 10),   pay_late=0.02),
        "watch":     dict(adopt=(0.55, 0.80), engage=(40, 75),  support=(70, 90),
                          nps=(6, 8),    pay_late=0.10),
        "at_risk":   dict(adopt=(0.35, 0.60), engage=(15, 45),  support=(45, 70),
                          nps=(3, 6),    pay_late=0.35),
        "critical":  dict(adopt=(0.05, 0.35), engage=(0, 20),   support=(15, 45),
                          nps=(0, 4),    pay_late=0.55),
        "expansion": dict(adopt=(0.80, 1.00), engage=(80, 100), support=(90, 100),
                          nps=(9, 10),   pay_late=0.00),
        "churned":   dict(adopt=(0.10, 0.40), engage=(0, 20),   support=(20, 50),
                          nps=(0, 3),    pay_late=0.40),
    }[arch]
    # jitter leve para no quedar determinista / slight jitter
    for k in ("adopt", "engage", "support"):
        lo, hi = p[k]
        p[k] = round(rng.uniform(lo, hi), 2)
    p["nps"] = rng.randint(p["nps"][0], p["nps"][1])
    return p


def _make_account(rng, idx, name):
    arch = rng.choices(ARCHETYPES, weights=ARCHETYPE_WEIGHTS)[0]
    tier = _pick_tier(rng)
    lo, hi = TIER_ARR[tier]
    arr_now = rng.randint(lo // 1000, hi // 1000) * 1000

    seats = rng.randint(*_tier_seats(tier))
    prof = _profile_for(arch, rng)
    active_seats = round(seats * rng.uniform(prof["adopt"] - 0.1, prof["adopt"] + 0.1))
    active_seats = max(1, min(seats, active_seats))
    login_freq = round(rng.uniform(prof["adopt"] * 5, min(5.0, prof["adopt"] * 5 + 0.6)), 1)
    feature_adoption = round(rng.uniform(prof["adopt"] * 100, min(100, prof["adopt"] * 100 + 10)))

    last_touch_days = rng.randint(0, 180)
    touches_90d = rng.randint(0, 12)
    qbr_attended = rng.random() < prof["engage"] / 100.0

    open_critical = rng.randint(0, 5)
    sla_compliance = round(rng.uniform(prof["support"], min(100.0, prof["support"] + 8)))
    avg_resolution_hours = round(rng.uniform(4, 96), 1)

    payment_status = "late" if rng.random() < prof["pay_late"] else "current"
    nps = prof["nps"]

    # Comercial: ARR previo y renovación / previous ARR and renewal
    if arch == "churned":
        arr_prev = arr_now
        arr_now = 0
        renewal_status = "lost"
    elif arch == "expansion":
        arr_prev = round(arr_now / rng.uniform(1.15, 1.4))
        renewal_status = "won"
    elif arch in ("healthy", "watch"):
        arr_prev = arr_now
        renewal_status = "won"
    else:
        arr_prev = arr_now
        renewal_status = rng.choices(["won", "pending", "lost"], weights=[0.5, 0.4, 0.1])[0]

    today = datetime.date.today()
    renewal_date = today + datetime.timedelta(days=rng.randint(-90, 270))
    signup_date = today - datetime.timedelta(days=rng.randint(180, 1800))

    return {
        "id": f"ACC-{idx:03d}",
        "name": name,
        "industry": rng.choice(INDUSTRIES),
        "region": rng.choice(REGIONS),
        "tier": tier,
        "arr": arr_now,
        "arr_prev": arr_prev,
        "seats": seats,
        "active_seats": active_seats,
        "login_freq": login_freq,
        "feature_adoption": round(feature_adoption),
        "last_touch_days": last_touch_days,
        "touches_90d": touches_90d,
        "qbr_attended": qbr_attended,
        "open_critical": open_critical,
        "sla_compliance": sla_compliance,
        "avg_resolution_hours": avg_resolution_hours,
        "payment_status": payment_status,
        "nps": nps,
        "renewal_status": renewal_status,
        "renewal_date": renewal_date.isoformat(),
        "signup_date": signup_date.isoformat(),
        "csm_owner": rng.choice(["Alex Rivera", "Sam Chen", "Dana Brooks", "Leo Martins"]),
    }


def generate(seed, n):
    rng = random.Random(seed)
    # nombres únicos / unique names
    used = set()
    accounts = []
    i = 0
    while len(accounts) < n and i < 10_000:
        name = f"{rng.choice(NAME_A)} {rng.choice(NAME_B)}"
        i += 1
        if name in used:
            continue
        used.add(name)
        accounts.append(_make_account(rng, len(accounts) + 1, name))

    return {
        "meta": {
            "title": "Customer Health Score — Cartera sintética · Synthetic portfolio",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "seed": seed,
            "accounts": len(accounts),
            "note": "100% fictional data — no real customers, companies or figures.",
        },
        "accounts": accounts,
    }


def main():
    ap = argparse.ArgumentParser(description="Genera cartera CSM sintética")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--accounts", type=int, default=60)
    ap.add_argument("--out", default="data/portfolio_raw.json")
    args = ap.parse_args()

    import os
    os.makedirs("data", exist_ok=True)
    portfolio = generate(args.seed, args.accounts)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(portfolio['accounts'])} cuentas -> {args.out}")


if __name__ == "__main__":
    main()
