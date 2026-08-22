# 🧠 Strategic Memory CRM

<div align="center">

[![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6366f1?style=for-the-badge&logo=anthropic&logoColor=white)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.2+-blue?style=for-the-badge&logo=python)](https://networkx.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-10b981?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25%20Passed-success?style=for-the-badge&logo=pytest&logoColor=white)](tests/test_crm.py)
[![GitHub Stars](https://img.shields.io/github/stars/adacreativeco/strategic-memory-crm?style=for-the-badge&color=ffd700)](https://github.com/adacreativeco/strategic-memory-crm/stargazers)
[![Release](https://img.shields.io/badge/Release-v1.1.0-6366f1?style=for-the-badge)](https://github.com/adacreativeco/strategic-memory-crm/releases)

<br/>

**Relationship intelligence over transaction storage.**

[English Documentation](README.md) • [🇹🇷 Türkçe Dokümantasyon](README.tr.md)

</div>

---

A lightweight behavioral intelligence CRM platform and **Model Context Protocol (MCP) Server** that models **trust dynamics, negotiation patterns, influence structures, organizational politics, and relationship risk** — instead of just storing deals and sales pipelines.

Built for strategists, executives, and AI agents navigating complex stakeholder ecosystems where ***who trusts whom* matters more than *who bought what***.

---

## 📸 Visual Showcase

<div align="center">

### 📊 Behavioral Intelligence & Relationship Matrix Dashboard
![Strategic CRM Dashboard](dashboard_screenshot.png)

<br/>

### 🕸️ Interactive Stakeholder Network Graph & Power Structures
![Stakeholder Network Graph](graph_screenshot.png)

<br/>

### 🎯 Deep Stakeholder Profile & AI Strategic Advisor Battleplan
![Stakeholder Profile and AI Strategic Advisor](stakeholder_screenshot.png)

</div>

---

## 🔌 Model Context Protocol (MCP) Server

Strategic Memory CRM exposes a full **AI Relationship Memory Layer** via MCP. AI assistants in **Claude Desktop**, **Cursor**, **VS Code**, or **Antigravity** can directly query behavioral profiles, calculate negotiation risk, inspect political power structures, and generate pre-meeting tactical briefings.

### 🛠️ Exposed MCP Tools

| MCP Tool | Description |
|---|---|
| `list_stakeholders` | List all stakeholders with role, organization, tier, personality traits, and risk level. |
| `get_stakeholder_intel` | Deep-dive profile on an individual (trust ties, negotiation style, reliability, risk drivers, allies/rivals). |
| `get_organization_politics` | NetworkX-driven structural power map (informal influencers via PageRank, gatekeepers, brokers, coalitions). |
| `analyze_relationship` | Dyadic relationship analysis (directional trust, favor ledger, entropy, interaction timeline). |
| `log_interaction` | Record meetings, calls, commitments, and favors with dynamic trust decay and reciprocity updates. |
| `add_stakeholder` | Create new stakeholders in the strategic memory database. |
| `generate_tactical_briefing` | Instant pre-meeting psychometric negotiation battleplan and strategic leverage points. |

### 🚀 Claude Desktop & Cursor Setup

Add the following to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "strategic-memory-crm": {
      "command": "python",
      "args": ["G:/git@adacreativeco/strategic-memory-crm/mcp_server.py"]
    }
  }
}
```

---

## 🚀 Key Features

### 1. 🧠 Behavioral Intelligence Engine
- **Trust Dynamics (`trust.py`):** Asymmetric trust scoring, continuous time-based passive decay, reciprocity balance, and personality compatibility.
- **Negotiation Profiling (`negotiation.py`):** Dominator, accommodator, collaborator, competitor, avoider styles; detects serial promise-breakers and chronic yielders.
- **Influence & Organizational Politics (`influence.py`):** NetworkX-powered PageRank, betweenness centrality, hidden coalition detection, gatekeepers, and brokers (articulation points).
- **Relationship Entropy (`entropy.py`):** Information-theoretic unpredictability measurement via Shannon entropy, trust delta volatility, and interaction regularity.
- **Composite Risk Assessment (`risk.py`):** Relationship and stakeholder risk scores with actionable factors and tactical recommendations.

### 2. ⚡ AI Strategic Advisor (Tactical Briefing Generator)
- Generates high-stakes pre-meeting negotiation battleplans directly on any stakeholder page (`POST /api/advisor/briefing` or via MCP `generate_tactical_briefing`).
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

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/adacreativeco/strategic-memory-crm.git
cd strategic-memory-crm
pip install -r requirements.txt
```

### 2. Run the Web Dashboard
```bash
python app.py
```
Open [http://localhost:5088](http://localhost:5088) in your browser.

### 3. Run the MCP Server (Stdio)
```bash
python mcp_server.py
```

### 4. Run Automated Tests
```bash
python -m unittest discover tests
```

---

## 📂 Architecture

```
strategic-memory-crm/
├── app.py                          # Flask web dashboard & REST APIs
├── mcp_server.py                   # Model Context Protocol (MCP) server entry point
├── strategic_memory_crm/
│   ├── models.py                   # Core dataclasses (Stakeholder, Interaction, Relationship, CRMState)
│   ├── storage.py                  # JSON persistence load & save engine
│   ├── trust.py                    # Trust dynamics & passive decay engine
│   ├── negotiation.py              # Behavioral profiling & pattern detection
│   ├── influence.py                # Graph centrality, gatekeepers, brokers & coalitions
│   ├── entropy.py                  # Shannon entropy & relationship volatility
│   ├── risk.py                     # Composite risk assessment & recommendations
│   ├── mcp_tools.py                # Modular MCP behavioral intelligence tools
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
│   ├── test_crm.py                 # Core CRM unit test suite
│   └── test_mcp.py                 # MCP server and tools unit test suite
├── data/                           # Persistent state directory (crm_state.json)
└── requirements.txt                # Dependencies (Flask, NetworkX, NumPy, SciPy, MCP)
```

---

## 📄 License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.

---

<div align="center">
Built with 🧠 by <a href="https://github.com/adacreativeco">ADA Creative Co.</a>
</div>
