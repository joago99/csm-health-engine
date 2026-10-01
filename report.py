#!/usr/bin/env python3
"""
Reporte de cartera estilo QBR (bilingüe ES/EN).
QBR-style portfolio report (bilingual ES/EN).

Lee data/portfolio.json y emite un resumen de salud de la cartera:
Reads data/portfolio.json and prints a portfolio health summary:

  - NRR / GRR, churn (logo y revenue), expansión / expansion
  - Distribución de salud / health distribution
  - Cuentas en riesgo (At-risk + Critical) / at-risk accounts
  - Próximas renovaciones / upcoming renewals

Uso / Usage:
    python report.py            # resumen completo / full summary
    python report.py --risk     # solo cuentas en riesgo / at-risk only
"""
import argparse
import json
import os
from datetime import date

_BASE = os.path.dirname(os.path.abspath(__file__))


def _fmt_money(v):
    if v >= 1_000_000:
        return f"${v/1_000_000:,.2f}M"
    if v >= 1_000:
        return f"${v/1_000:,.0f}K"
    return f"${v:,.0f}"


def _fmt_pct(v):
    return f"{v*100:,.1f}%"


def load():
    with open(os.path.join(_BASE, "data", "portfolio.json"), encoding="utf-8") as f:
        return json.load(f)


def print_header(s):
    print()
    print("=" * 62)
    print(f"  {s}")
    print("=" * 62)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--risk", action="store_true", help="solo cuentas en riesgo / at-risk only")
    args = ap.parse_args()

    data = load()
    s = data["summary"]
    accts = data["accounts"]

    print_header("RESUMEN DE CARTERA · PORTFOLIO SUMMARY")
    print(f"  Cuentas · Accounts          : {s['total_accounts']}")
    print(f"  ARR total                   : {_fmt_money(s['total_arr'])}")
    print(f"  NRR (retención neta) · NRR  : {_fmt_pct(s['nrr'])}")
    print(f"  GRR (retención bruta) · GRR : {_fmt_pct(s['grr'])}")
    print(f"  Churn logo · Logo churn     : {_fmt_pct(s['logo_churn'])}")
    print(f"  Churn revenue · Rev churn   : {_fmt_pct(s['revenue_churn'])}")
    print(f"  Expansión · Expansion       : {_fmt_money(s['expansion'])}")
    print(f"  QBR coverage                : {_fmt_pct(s['qbr_coverage'])}")
    print(f"  SLA compliance              : {s['sla_compliance']:.1f}%")

    print_header("SALUD · HEALTH DISTRIBUTION")
    for level in ("Healthy", "Watch", "At-risk", "Critical"):
        n = s["health_distribution"][level]
        bar = "#" * n
        print(f"  {level:<10} {n:>3}  {bar}")

    print_header("ARR EN RIESGO · ARR AT RISK")
    print(f"  Cuentas at-risk · At-risk accounts : {s['at_risk_count']}")
    print(f"  ARR en riesgo · ARR at risk        : {_fmt_money(s['arr_at_risk'])}")

    print_header("ARR POR TIER · ARR BY TIER")
    for tier in ("Strategic", "Enterprise", "Growth", "SMB"):
        print(f"  {tier:<12} {_fmt_money(s['arr_by_tier'][tier])}")

    if args.risk:
        at_risk = [a for a in accts if a["risk"] in ("At-risk", "Critical")]
        at_risk.sort(key=lambda a: a["health"])
        print_header("CUENTAS EN RIESGO · AT-RISK ACCOUNTS")
        print(f"  {'Salud · Health':<13} {'Riesgo · Risk':<11} {'Tier':<12} {'ARR':>12}  Cuenta · Account")
        for a in at_risk:
            print(f"  {a['health']:<13} {a['risk']:<11} {a['tier']:<12} "
                  f"{_fmt_money(a['arr']):>12}  {a['name']}")

    upcoming = sorted(
        [a for a in accts if a["arr"] > 0 and a["renewal_date"] >= date.today().isoformat()],
        key=lambda a: a["renewal_date"],
    )[:10]
    print_header("PRÓXIMAS RENOVACIONES · UPCOMING RENEWALS")
    for a in upcoming:
        print(f"  {a['renewal_date']}  {_fmt_money(a['arr']):>10}  {a['name']} "
              f"({a['risk']})")
    print()


if __name__ == "__main__":
    main()
