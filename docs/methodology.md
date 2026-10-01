# Customer Health Score — Metodología · Methodology

Customer Success consiste en anticiparse al churn y maximizar la retención y expansión.
Esta metodología operacionaliza ese trabajo en una métrica única (health 0-100), niveles de
riesgo accionables y playbooks concretos. Todo está implementado en `health.py` sobre datos
sintéticos.

Customer Success is about anticipating churn and maximizing retention and expansion.
This methodology turns that work into a single metric (health 0-100), actionable risk levels
and concrete playbooks — all implemented in `health.py` over synthetic data.

---

## 1. Dimensiones y pesos · Dimensions & weights

El health score pondera cinco dimensiones. / The health score weights five dimensions.

| Dimensión · Dimension | Peso · Weight | Qué mide · What it measures |
|---|---|---|
| Adopción · Adoption | 30% | Uso real del producto / actual product usage |
| Engagement · Engagement | 20% | Calidad de la relación / relationship quality |
| Soporte · Support | 20% | Salud de tickets y SLA / ticket & SLA health |
| Comercial · Commercial | 20% | Estado de pago y renovación / payment & renewal |
| Sentimiento · Sentiment | 10% | NPS / CSAT |

La adopción pesa más porque es el predictor líder de renovación en productos B2B de
suscripción: un cliente que no usa el producto, no renueva.

Adoption weighs most because it is the leading predictor of renewal in subscription B2B:
a customer that doesn't use the product won't renew.

## 2. Rúbrica por dimensión · Rubric per dimension

| Dimensión · Dimension | Señales · Signals | Cálculo · Formula (0-100) |
|---|---|---|
| Adopción | `active_seats/seats`, `login_freq`, `feature_adoption` | 50% seats · 30% logins · 20% features |
| Engagement | `last_touch_days`, `touches_90d`, `qbr_attended` | 40% recencia · 35% cadencia · 25% QBR |
| Soporte | `open_critical`, `sla_compliance`, `avg_resolution_hours` | 40% críticos · 40% SLA · 20% velocidad |
| Comercial | `payment_status`, `renewal_status` | 60% pago · 40% renovación |
| Sentimiento | `nps` (0-10) | `nps × 10` |

## 3. Niveles de riesgo · Risk levels

| Nivel · Level | Rango · Range | Lectura · Reading |
|---|---|---|
| Healthy | 70-100 | Renueva y crece · renews & expands |
| Watch | 50-69 | Monitorear · monitor |
| At-risk | 30-49 | Requiere plan de éxito · needs a success plan |
| Critical | 0-29 | Escalar ya · escalate now |

## 4. Segmentación por tier · Tiering

El tier determina el nivel de servicio, no el health. / Tier drives service level, not health.

| Tier | ARR (USD) | Enfoque · Focus |
|---|---|---|
| Strategic | ≥ 200K | Patrocinador ejecutivo, QBR trimestral · exec sponsor, quarterly QBR |
| Enterprise | 50K-199K | CSM dedicado, plan de éxito · dedicated CSM, success plan |
| Growth | 10K-49K | Escala 1:many, automatización · 1:many, automation |
| SMB | < 10K | Self-serve + digital touch · self-serve + digital |

## 5. Métricas de cartera · Portfolio metrics

| Métrica · Metric | Fórmula · Formula | Qué indica · What it indicates |
|---|---|---|
| NRR (Net Revenue Retention) | `ARR actual / ARR inicial` | Retención neta incluyendo expansión · net retention incl. expansion |
| GRR (Gross Revenue Retention) | `(ARR actual − expansión) / ARR inicial` | Retención sin expansión · retention without expansion |
| Logo churn | `cuentas perdidas / cuentas iniciales` | Pérdida de clientes · customer loss |
| Revenue churn | `ARR perdido / ARR inicial` | Pérdida de ingresos · revenue loss |
| Expansión · Expansion | `Σ max(0, ARR actual − ARR previo)` | Upsell / cross-sell |
| QBR coverage | `cuentas con QBR / total` | Disciplina de revisión · review discipline |
| SLA compliance | `media de cumplimiento SLA` | Calidad operativa · operational quality |

Un NRR > 100% significa que la cartera crece solo por expansión, incluso con churn.
NRR above 100% means the portfolio grows from expansion alone, even with churn.

## 6. Disparadores de churn · Churn triggers

Señales líderes que preceden al churn (todas capturadas por las dimensiones):
Leading indicators that precede churn (all captured by the dimensions):

- **Caída de adopción** · usage decline: logins o seats activos bajando 3 meses seguidos.
- **Soporte roto** · broken support: tickets críticos abiertos > 7 días o SLA < 80%.
- **Silencio** · silence: sin touchpoint relevante en 90+ días, QBR rechazada.
- **Comercial débil** · weak commercial: pago atrasado o renovación "pending" a < 30 días.
- **NPS promotor → detractor** · promoter → detractor drift.

## 7. Playbooks · Playbooks

Acción por nivel de riesgo. / Action per risk level.

**Critical (0-29)**
- Escalar a patrocinador ejecutivo en < 24 h · escalate to exec sponsor in < 24 h.
- Armar plan de salvataje con dueño y fecha · build a save plan with owner + date.
- Cadencia semanal interna + bisemanal con el cliente · weekly internal + biweekly client cadence.

**At-risk (30-49)**
- Crear plan de éxito con hitos medibles · create a success plan with measurable milestones.
- Revisión semanal de adopción con el equipo del cliente · weekly adoption review with client team.
- Remover fricción: resolver tickets críticos como prioridad · remove friction: fix critical tickets first.

**Watch (50-69)**
- Check-in proactivo y educación de features · proactive check-in + feature education.
- QBR para alinear valor y roadmap · QBR to align on value & roadmap.

**Healthy (70-100)**
- Buscar expansión (upsell/cross-sell) · pursue expansion (upsell/cross-sell).
- Pedir referencia, caso de estudio y advocacy · ask for reference, case study and advocacy.

## 8. Uso del repo · Using the repo

```
python generate_data.py --accounts 60     # cartera sintética · synthetic portfolio
python health.py                          # score + métricas · scoring + metrics
python report.py                          # resumen QBR · QBR summary
python -m http.server 8099                # dashboard en · dashboard at localhost:8099/dashboard/
```

Los datos son 100% ficticios; la metodología es aplicable a cualquier cartera B2B de suscripción.
Data is 100% fictional; the methodology applies to any subscription B2B portfolio.
