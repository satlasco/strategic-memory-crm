# Strategic Memory CRM

🇹🇷 [Türkçe Dokümantasyon](README.tr.md)

> Relationship intelligence over transaction storage.

A lightweight, behavioral intelligence CRM platform that models **trust dynamics, negotiation patterns, influence structures, organizational politics, and relationship risk** — instead of just storing deals and sales pipelines.

Built for strategists, executives, and leaders navigating complex stakeholder ecosystems where *who trusts whom* matters more than *who bought what*.

---

## 🚀 Key Features

### 1. 🧠 Behavioral Intelligence Engine
- **Trust Dynamics (`trust.py`):** Asymmetric trust scoring, continuous time-based passive decay, reciprocity balance, and personality compatibility.
- **Negotiation Profiling (`negotiation.py`):** Dominator, accommodator, collaborator, competitor, avoider styles; serial promise-breakers and chronic yielders detection.
- **Influence & Organizational Politics (`influence.py`):** NetworkX-powered PageRank, betweenness centrality, hidden coalition detection, gatekeepers, and brokers (articulation points).
- **Relationship Entropy (`entropy.py`):** Information-theoretic unpredictability measurement via Shannon entropy, trust delta volatility, and interaction regularity.
- **Composite Risk Assessment (`risk.py`):** Relationship and stakeholder risk scores with actionable factors and tactical recommendations.

### 2. ⚡ AI Strategic Advisor (Tactical Briefing Generator)
- Generates high-stakes pre-meeting negotiation battleplans directly on any stakeholder page (`POST /api/advisor/briefing`).
- Supported AI engines:
  - 🟢 **Built-in Tactical Engine (Offline / Instant):** Deep heuristic rules & psychometric analysis.
  - ✨ **Google Gemini:** `gemini-2.0-flash`, `gemini-1.5-pro`
  - 🧠 **OpenAI:** `gpt-4o-mini`, `gpt-4o`, `o3-mini`
  - ⚡ **Anthropic Claude:** `claude-3-5-sonnet-20241022`

### 3. 💾 Data Persistence & Write APIs
- Real-time JSON persistence (`data/crm_state.json`).
- `POST /api/interaction` — Log meetings, calls, negotiations, favors, or conflicts with automatic incremental trust updates.
- `POST /api/stakeholder` — Add new stakeholders dynamically.
- `POST /api/reset` — Reset dataset to the baseline scenario.

### 4. 🔌 Dynamic Port Conflict Management
- Starts on port `5088` by default with automatic port fallback (`5089`, `5090`...) if the port is in use.

---

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
git clone https://github.com/adacreativeco/strategic-memory-crm.git
cd strategic-memory-crm
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
python app.py
```
Open [http://localhost:5088](http://localhost:5088) in your browser.

### 3. Run Automated Tests
```bash
python -m unittest tests/test_crm.py
```

---

## 📂 Architecture

```
strategic-memory-crm/
├── app.py                          # Flask web dashboard & REST APIs
├── strategic_memory_crm/
│   ├── models.py                   # Core dataclasses (Stakeholder, Interaction, Relationship, CRMState)
│   ├── storage.py                  # JSON persistence load & save engine
│   ├── trust.py                    # Trust dynamics & passive decay engine
│   ├── negotiation.py              # Behavioral profiling & pattern detection
│   ├── influence.py                # Graph centrality, gatekeepers, brokers & coalitions
│   ├── entropy.py                  # Shannon entropy & relationship volatility
│   ├── risk.py                     # Composite risk assessment & recommendations
│   ├── graph.py                    # Vis.js JSON graph serialization
│   ├── simulation.py               # Interaction history simulator
│   └── dataset.py                  # Fictional M&A dataset generator
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Dark-themed master layout
│   ├── dashboard.html              # Matrix, stats & interaction/stakeholder modals
│   ├── stakeholder.html            # Profile, timeline & AI Strategic Advisor
│   └── graph.html                  # Interactive Vis.js network graph
├── static/
│   └── style.css                   # Responsive dark UI styling
├── tests/
│   └── test_crm.py                 # Comprehensive unit test suite (18 tests)
├── data/                           # Persistent state directory (crm_state.json)
└── requirements.txt                # Dependencies (Flask, NetworkX, NumPy)
```

---

## 📄 License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.
