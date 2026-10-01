# CSM Health Engine

**ES** · **EN** (bilingüe / bilingual)

Motor de **Customer Health Score** para equipos de Customer Success: convierte una cartera de
cuentas en una métrica de salud accionable (0-100), niveles de riesgo, segmentación por tier y
métricas de retención (NRR, GRR, churn, expansión). Incluye dashboard web.

A **Customer Health Score** engine for Customer Success teams: turns an account portfolio into an
actionable health metric (0-100), risk levels, tier segmentation and retention metrics (NRR, GRR,
churn, expansion). Includes a web dashboard.

> **Datos 100% sintéticos.** Ninguna empresa, monto ni persona es real. La metodología es lo
> reutilizable. · **100% synthetic data.** No real company, amount or person. The reusable part is
> the methodology.

---

## Qué demuestra · What it demonstrates

- **Pensar en CSM** · CSM thinking: health score, churn, expansión y playbooks — no solo "responder tickets".
- **Analítica** · Analytics: scoring ponderado por 5 dimensiones, NRR/GRR, churn logo vs revenue.
- **Full-stack** · Full-stack: pipeline Python (stdlib) + dashboard Chart.js sin dependencias de build.

## Pipeline

```
generate_data.py   →  data/portfolio_raw.json   (cartera sintética · synthetic portfolio)
health.py          →  data/portfolio.json       (score 0-100 + riesgo + tier + métricas)
report.py          →  resumen QBR en consola     (QBR summary on console)
dashboard/index.html → dashboard web (lee data/portfolio.json · reads it)
```

## Cómo correr · How to run

```bash
pip install -r requirements.txt   # solo para el dashboard local · only for local dashboard
python generate_data.py           # genera datos · generate data
python health.py                  # calcula scores · compute scores
python report.py                  # resumen QBR · QBR summary
python -m http.server 8099        # dashboard → http://localhost:8099/dashboard/
```

> `generate_data.py`, `health.py` y `report.py` usan **solo la stdlib** (sin pandas). El dashboard
> usa Chart.js (vendoreado en `dashboard/vendor/`). · The Python scripts use **stdlib only** (no
> pandas). The dashboard uses vendored Chart.js.

## Dashboard

Tema claro · light theme. Muestra / shows:

- KPIs: ARR total, NRR, GRR, en riesgo, churn, expansión, QBR coverage, SLA.
- Distribución de salud · health distribution (bar).
- ARR por tier · ARR by tier (bar).
- Tabla de cuentas en riesgo · at-risk accounts table.
- Próximas renovaciones · upcoming renewals.

## Estructura · Structure

```
csm-health-engine/
├── generate_data.py        # cartera sintética determinística · deterministic synthetic portfolio
├── health.py               # motor de health score + métricas · scoring engine + metrics
├── report.py               # resumen QBR CLI · CLI QBR summary
├── dashboard/
│   ├── index.html          # dashboard web
│   └── vendor/chart.umd.min.js
├── docs/methodology.md     # rúbrica, riesgos, tiers, métricas y playbooks
└── data/portfolio.json     # salida demo (commiteada) · committed demo output
```

## Metodología · Methodology

La documentación completa está en [`docs/methodology.md`](docs/methodology.md): dimensiones y pesos,
rúbrica de cálculo, niveles de riesgo, segmentación por tier, definición de métricas, disparadores
de churn y playbooks por nivel.

Full documentation in [`docs/methodology.md`](docs/methodology.md): dimensions & weights, scoring
rubric, risk levels, tiering, metric definitions, churn triggers and per-level playbooks.

## Disclaimer

Este proyecto es una demo de portafolio. No usa datos de ningún empleador ni cliente.
This is a portfolio demo. It uses no data from any employer or client.
