# Strategic Memory CRM

🇹🇷 [Türkçe Dokümantasyon](README.tr.md)

> Relationship intelligence over transaction storage.

A lightweight CRM prototype that models **behavioral intelligence** — trust dynamics, negotiation patterns, influence structures, organizational politics, and relationship risk — instead of storing deals and pipelines.

Built for strategists, operators, and anyone navigating complex stakeholder ecosystems where *who trusts whom* matters more than *who bought what*.

---

## What This Models

### Trust Dynamics
Trust is asymmetric, continuous, and time-dependent. It evolves through interaction history, commitment follow-through, reciprocity balance, and personality compatibility. Trust decays passively toward neutral when relationships go dormant.

### Negotiation Patterns
Stakeholders are profiled by their negotiation behavior — dominator, accommodator, collaborator, competitor, or avoider. The system detects serial promise-breakers, chronic yielders, pure escalators, and reciprocal dynamics between pairs.

### Influence Structures
Formal hierarchy meets informal power networks. PageRank, betweenness centrality, and closeness centrality identify who actually controls information flow. Coalition detection reveals hidden alliances; articulation point analysis finds the brokers holding the network together.

### Organizational Politics
Political vulnerability scoring flags stakeholders who are outranked by rivals, lack allies, depend on a single relationship, or sit isolated in the network. Power scores blend structural centrality with organizational tier and trust-weighted inbound connections.

### Relationship Entropy
An information-theoretic measure of relationship unpredictability. Combines Shannon entropy over sentiment history, trust delta volatility, and interaction regularity. High entropy = volatile and hard to read. Low entropy = stable and predictable (for better or worse).

### Relationship Risk
Composite risk assessment combining trust trajectory, entropy, reciprocity imbalance, political vulnerability, and dependency concentration. Each stakeholder gets actionable risk factors and recommendations.

---

## The Scenario

The included dataset simulates a **tech company acquisition** between Meridian Systems (acquirer) and Vantage Analytics (target). Twelve stakeholders span C-suite, VP, director, manager, and external advisory roles across both organizations:

| Stakeholder | Role | Organization |
|---|---|---|
| Diana Kessler | CEO | Meridian Systems |
| Robert Tanaka | CFO | Meridian Systems |
| Samira Okafor | VP Engineering | Meridian Systems |
| Marcus Webb | Director of Product | Meridian Systems |
| Linda Chen | Director of Operations | Meridian Systems |
| James Holloway | CEO (outgoing) | Vantage Analytics |
| Priya Sharma | CFO | Vantage Analytics |
| Elena Vasquez | VP Product | Vantage Analytics |
| Tomás Rivera | Engineering Lead | Vantage Analytics |
| Aisha Mbeki | Data Science Manager | Vantage Analytics |
| Catherine Blackwood | M&A Advisor | Blackwood & Associates |
| Philip Raines | Board Member | Meridian Board |

80 interactions are simulated across 6 months — meetings, negotiations, conflicts, favors, betrayals, collaborations — with realistic sentiment dynamics, commitment tracking, information flow, and power plays.

---

## Quick Start

```bash
# Clone
git clone https://github.com/adacreativeco/strategic-memory-crm.git
cd strategic-memory-crm

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python app.py
```

Open [http://localhost:5000](http://localhost:5000).

---

## Architecture

```
strategic-memory-crm/
├── app.py                          # Flask web dashboard
├── strategic_memory_crm/
│   ├── models.py                   # Core data models
│   ├── trust.py                    # Trust dynamics engine
│   ├── negotiation.py              # Negotiation pattern analysis
│   ├── influence.py                # Influence & org politics
│   ├── entropy.py                  # Relationship entropy scoring
│   ├── risk.py                     # Composite risk assessment
│   ├── graph.py                    # Stakeholder graph builder
│   ├── simulation.py               # Interaction history simulator
│   └── dataset.py                  # Fictional dataset generator
├── templates/                      # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── stakeholder.html
│   └── graph.html
├── static/
│   └── style.css                   # Dark-themed minimal UI
├── data/generated/                 # Generated JSON datasets
└── requirements.txt
```

### Modules

| Module | Purpose |
|---|---|
| `models.py` | Stakeholder, Interaction, Relationship, and CRMState dataclasses |
| `trust.py` | Trust scoring with decay, commitment tracking, reciprocity, personality compatibility |
| `negotiation.py` | Behavioral profiling (style classification, pattern detection, reciprocal pair analysis) |
| `influence.py` | NetworkX-powered centrality metrics, gatekeeper/broker detection, coalition finding, power scoring |
| `entropy.py` | Shannon entropy over sentiments, trust volatility, interaction regularity, composite scoring |
| `risk.py` | Per-relationship and per-stakeholder risk with factors and recommendations |
| `graph.py` | JSON graph serialization for front-end force-directed visualization |
| `simulation.py` | Weighted random interaction generator with personality-driven dynamics |
| `dataset.py` | Full scenario builder (stakeholders + simulation + scoring + JSON export) |

---

## Dashboard

The web UI provides three views:

### Dashboard Preview

#### Relationship Intelligence Dashboard
![Dashboard View](dashboard_screenshot.png)

#### Stakeholder Detail View
![Stakeholder Detail View](stakeholder_screenshot.png)

#### Stakeholder Network Graph
![Network Graph View](graph_screenshot.png)

### Relationship Intelligence Dashboard (`/`)
- Network-level stats: stakeholder count, interaction count, active relationships, network entropy
- Network intelligence: detected gatekeepers, brokers, coalitions, and reciprocal negotiation dynamics
- Stakeholder risk matrix with trust, power, risk scores, negotiation styles, and vulnerability flags

### Stakeholder Detail (`/stakeholder/<id>`)
- Influence metrics (power score, PageRank, betweenness centrality)
- Risk assessment with factors and actionable recommendations
- Personality profile visualization
- Negotiation profile (style, reliability, concession ratio, patterns)
- Relationship table with trust, entropy, risk, trajectory
- Interaction timeline with sentiment coloring, commitment tracking, information flow

### Stakeholder Network Graph (`/graph`)
- Force-directed graph with drag, pan, zoom
- Node size = influence (PageRank), node color = organization
- Edge color = trust level (green/orange/red), edge width = interaction frequency
- Hover for tooltips, double-click to navigate to stakeholder detail

---

## API Endpoints

All data is available as JSON for programmatic access:

| Endpoint | Description |
|---|---|
| `GET /api/state` | Full CRM state (stakeholders, interactions, relationships) |
| `GET /api/graph` | Graph data for visualization (nodes + edges) |
| `GET /api/entropy` | Network entropy + per-relationship entropy breakdowns |
| `GET /api/influence` | Centrality metrics, gatekeepers, brokers, coalitions, power scores |
| `GET /api/risk` | Per-stakeholder risk assessments with factors and recommendations |
| `GET /api/negotiations` | Negotiation profiles for all stakeholders |

---

## Concepts

### Trust Score (0–1)
Continuous, asymmetric. Updated by interaction sentiment, commitment follow-through, reciprocity, personality compatibility, and explicit trust deltas. Decays passively toward 0.5 (neutral) over time.

### Relationship Entropy (0–1)
Composite of:
- **Sentiment entropy** (0.45 weight): Shannon entropy over discretized sentiment observations
- **Trust volatility** (0.35 weight): Standard deviation of trust deltas
- **Interaction regularity** (0.20 weight): Coefficient of variation of inter-interaction timing

### Power Score
Weighted blend of:
- **PageRank** (0.40): Structural influence in the directed trust-weighted graph
- **Organizational tier** (0.30): Formal hierarchy position
- **Inbound trust** (0.30): Average trust score from other stakeholders

### Negotiation Styles
- **Dominator**: Frequent power plays, rarely concedes
- **Accommodator**: Concedes often, avoids confrontation
- **Collaborator**: Balanced give-and-take, high reliability
- **Competitor**: Pushes for advantage, moderate concessions
- **Avoider**: Low negotiation engagement

---

## Design Philosophy

This prototype deliberately avoids enterprise CRM complexity (pipelines, lead scoring, email integration, Salesforce-style workflows). Instead, it focuses on:

1. **Behavioral signal over transactional data** — What someone *does* in relationships reveals more than what they *buy*.
2. **Systems thinking** — Relationships exist in networks. A stakeholder's risk depends on the entire graph, not just their direct connections.
3. **Entropy as a first-class metric** — Unpredictability is itself a risk signal worth measuring.
4. **Asymmetric trust** — A trusts B ≠ B trusts A. Modeling this asymmetry captures real-world power dynamics.
5. **Political intelligence** — Formal hierarchy tells half the story. Informal influence, coalition dynamics, and brokerage tell the rest.

---

## Tech Stack

- **Python 3.10+**
- **Flask** — Minimal web framework
- **NetworkX** — Graph algorithms (PageRank, betweenness, community detection)
- **NumPy/SciPy** — Numerical computation
- **Vanilla JS + Canvas** — Force-directed graph visualization (no heavy frontend framework)

---

## License

Apache License 2.0 - Copyright 2026 Ada Creative Co. See [LICENSE](LICENSE) for details.
