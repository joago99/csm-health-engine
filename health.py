#!/usr/bin/env python3
"""
Motor de Customer Health Score.

Lee data/portfolio_raw.json, calcula para cada cuenta:
  - Health score 0-100 (5 dimensiones ponderadas)
  - Nivel de riesgo (Healthy / Watch / At-risk / Critical)
  - Tier (Strategic / Enterprise / Growth / SMB)
y las métricas de cartera (NRR, GRR, churn, expansión, QBR, SLA).

Escribe data/portfolio.json (para el dashboard y el reporte).

Uso / Usage:
    python health.py
"""
import json
import os

# ---------------------------------------------------------------------------
# Pesos de las 5 dimensiones / weights of the 5 dimensions
# ---------------------------------------------------------------------------
WEIGHTS = {
    "adoption": 0.30,     # uso del producto / product usage
    "engagement": 0.20,   # relación / relationship
    "support": 0.20,      # salud de tickets/SLA / support health
    "commercial": 0.20,   # salud comercial / commercial health
    "sentiment": 0.10,    # NPS/CSAT
}


def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def adoption_score(a):
    seat_ratio = a["active_seats"] / max(1, a["seats"])
    login = a["login_freq"] / 5.0
    feature = a["feature_adoption"] / 100.0
    return _clamp(100 * (0.5 * seat_ratio + 0.3 * login + 0.2 * feature))


def engagement_score(a):
    recency = _clamp(100 - a["last_touch_days"] * 0.8)
    cadence = _clamp(a["touches_90d"] * 10)
    qbr = 100 if a["qbr_attended"] else 50
    return _clamp(0.4 * recency + 0.35 * cadence + 0.25 * qbr)


def support_score(a):
    critical = _clamp(100 - a["open_critical"] * 25)
    sla = a["sla_compliance"]
    speed = _clamp(100 - a["avg_resolution_hours"] * 0.6)
    return _clamp(0.4 * critical + 0.4 * sla + 0.2 * speed)


def commercial_score(a):
    pay = 100 if a["payment_status"] == "current" else 40
    if a["renewal_status"] == "won":
        renewal = 100
    elif a["renewal_status"] == "pending":
        renewal = 55
    else:  # lost
        renewal = 0
    return _clamp(0.6 * pay + 0.4 * renewal)


def sentiment_score(a):
    return a["nps"] * 10.0  # NPS 0-10 -> 0-100


def health_score(a):
    subs = {
        "adoption": adoption_score(a),
        "engagement": engagement_score(a),
        "support": support_score(a),
        "commercial": commercial_score(a),
        "sentiment": sentiment_score(a),
    }
    total = sum(WEIGHTS[k] * subs[k] for k in WEIGHTS)
    return round(_clamp(total)), {k: round(v) for k, v in subs.items()}


def risk_level(score):
    if score >= 70:
        return "Healthy"
    if score >= 50:
        return "Watch"
    if score >= 30:
        return "At-risk"
    return "Critical"


def tier_of(arr):
    if arr >= 200_000:
        return "Strategic"
    if arr >= 50_000:
        return "Enterprise"
    if arr >= 10_000:
        return "Growth"
    return "SMB"


def portfolio_metrics(accounts):
    total_arr = sum(a["arr"] for a in accounts)
    start_arr = sum(a["arr_prev"] for a in accounts if a["arr_prev"] > 0)

    churned = [a for a in accounts if a["renewal_status"] == "lost" and a["arr"] == 0]
    expansion = sum(max(0, a["arr"] - a["arr_prev"]) for a in accounts)
    contraction = sum(max(0, a["arr_prev"] - a["arr"]) for a in accounts if a["arr"] > 0)

    n_accounts = max(1, len([a for a in accounts if a["arr_prev"] > 0]))
    logo_churn = len(churned) / n_accounts
    revenue_churn = sum(a["arr_prev"] for a in churned) / max(1, start_arr)
    nrr = (total_arr) / max(1, start_arr)
    grr = (total_arr - expansion) / max(1, start_arr)

    at_risk = [a for a in accounts if a.get("risk") in ("At-risk", "Critical")]
    arr_at_risk = sum(a["arr"] for a in at_risk)
    qbr_den = max(1, len(accounts))
    qbr_cov = sum(1 for a in accounts if a["qbr_attended"]) / qbr_den
    sla = sum(a["sla_compliance"] for a in accounts) / max(1, len(accounts))

    health_dist = {"Healthy": 0, "Watch": 0, "At-risk": 0, "Critical": 0}
    for a in accounts:
        health_dist[a["risk"]] += 1

    arr_by_tier = {"Strategic": 0, "Enterprise": 0, "Growth": 0, "SMB": 0}
    for a in accounts:
        arr_by_tier[a["tier"]] += a["arr"]

    return {
        "total_accounts": len(accounts),
        "total_arr": total_arr,
        "start_arr": start_arr,
        "arr_by_tier": arr_by_tier,
        "health_distribution": health_dist,
        "at_risk_count": len(at_risk),
        "arr_at_risk": arr_at_risk,
        "nrr": round(nrr, 4),
        "grr": round(grr, 4),
        "logo_churn": round(logo_churn, 4),
        "revenue_churn": round(revenue_churn, 4),
        "expansion": expansion,
        "contraction": contraction,
        "qbr_coverage": round(qbr_cov, 4),
        "sla_compliance": round(sla, 1),
    }


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base, "data", "portfolio_raw.json")
    out_path = os.path.join(base, "data", "portfolio.json")

    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)

    accounts = raw["accounts"]
    for a in accounts:
        score, dims = health_score(a)
        a["health"] = score
        a["risk"] = risk_level(score)
        a["dims"] = dims
        a["tier"] = tier_of(a["arr"])  # tier por ARR real, no por la señal

    summary = portfolio_metrics(accounts)

    out = {
        "meta": raw["meta"],
        "summary": summary,
        "accounts": accounts,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK: {summary['total_accounts']} cuentas scoreadas -> {out_path}")
    print(f"     NRR={summary['nrr']:.1%}  GRR={summary['grr']:.1%}  "
          f"at-risk={summary['at_risk_count']}  logo_churn={summary['logo_churn']:.1%}")


if __name__ == "__main__":
    main()
