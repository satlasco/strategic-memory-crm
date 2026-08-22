# 🧠 Strategic Memory CRM

<div align="center">

[![MCP](https://img.shields.io/badge/MCP-Model_Context_Protocol-6366f1?style=for-the-badge&logo=anthropic&logoColor=white)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.2+-blue?style=for-the-badge&logo=python)](https://networkx.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-10b981?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25%20Geçti-success?style=for-the-badge&logo=pytest&logoColor=white)](tests/test_crm.py)
[![GitHub Stars](https://img.shields.io/github/stars/adacreativeco/strategic-memory-crm?style=for-the-badge&color=ffd700)](https://github.com/adacreativeco/strategic-memory-crm/stargazers)
[![Release](https://img.shields.io/badge/Sürüm-v1.1.0-6366f1?style=for-the-badge)](https://github.com/adacreativeco/strategic-memory-crm/releases)

<br/>

**İşlem depolamak yerine ilişki ve davranış zekası yönetimi.**

[🇹🇷 Türkçe Dokümantasyon](README.tr.md) • [🇺🇸 English Documentation](README.md)

</div>

---

Yalnızca satış anlaşmalarını ve boru hatlarını (pipeline) tutmak yerine **güven dinamiklerini, müzakere modellerini, etki yapılarını, organizasyonel politikayı ve ilişki riskini** modelleyen davranışsal zeka CRM platformu ve **Model Context Protocol (MCP) Sunucusu**.

Kimin kime güvendiğinin kimin ne satın aldığından daha önemli olduğu karmaşık paydaş ekosistemlerinde stratejistler, yöneticiler ve yapay zekâ ajanları için tasarlanmıştır.

---

## 📸 Görsel Vitrin

<div align="center">

### 📊 Davranışsal Zeka & İlişki Matrisi Kontrol Paneli
![Strategic CRM Dashboard](dashboard_screenshot.png)

<br/>

### 🕸️ Etkileşimli Paydaş Ağ Grafiği & Güç Yapıları
![Stakeholder Network Graph](graph_screenshot.png)

<br/>

### 🎯 Detaylı Paydaş Profili & Yapay Zeka Taktiksel Savaş Planı
![Stakeholder Profile and AI Strategic Advisor](stakeholder_screenshot.png)

</div>

---

## 🔌 Model Context Protocol (MCP) Sunucusu

Strategic Memory CRM, yapay zekâ asistanları için **Stratejik İlişki Hafıza Katmanı** sunar. **Claude Desktop**, **Cursor**, **VS Code** veya **Antigravity** içinden doğrudan paydaş profillerini sorgulayabilir, müzakere risklerini hesaplayabilir, güç haritalarını inceleyebilir ve toplantı öncesi taktiksel brifingler üretebilirsiniz.

### 🛠️ Erişilebilir MCP Araçları

| MCP Aracı | Açıklama |
|---|---|
| `list_stakeholders` | Tüm paydaşları unvan, şirket, hiyerarşi, kişilik özellikleri ve risk puanıyla listeler. |
| `get_stakeholder_intel` | Bir paydaş hakkında derin istihbarat sunar (güven bağları, müzakere stili, güvenilirlik, risk faktörleri, müttefik/rakipler). |
| `get_organization_politics` | NetworkX destekli yapısal güç haritasını çıkarır (PageRank ile gayriresmi liderler, bilgi bekçileri, aracılar, koalisyonlar). |
| `analyze_relationship` | İki kişi arasındaki ikili ilişkiyi analiz eder (yönlü güven, iyilik dengesi, entropi/volatilite, etkileşim geçmişi). |
| `log_interaction` | Yeni görüşme, arama veya taahhütleri dinamik güven sönümlemesi ve karşılıklılık güncellemeleriyle kaydeder. |
| `add_stakeholder` | Stratejik hafıza veritabanına yeni bir paydaş ekler. |
| `generate_tactical_briefing` | Toplantı öncesi anlık psikometrik müzakere savaş planı ve taktiksel kaldıraç noktaları üretir. |

### 🚀 Claude Desktop & Cursor Kurulumu

`claude_desktop_config.json` veya Cursor MCP ayarlarına ekleyin:

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

## 🚀 Öne Çıkan Özellikler

### 1. 🧠 Davranışsal Zeka Motoru
- **Güven Dinamikleri (`trust.py`):** Asimetrik güven puanlama, zamana bağlı sönümleme (passive decay), karşılıklılık dengesi ve kişilik uyumu.
- **Müzakere Profili (`negotiation.py`):** Dominant, işbirlikçi, taviz veren ve kaçınmacı stiller; sözünden dönenler (promise-breakers) ve kronik tavizcilerin tespiti.
- **Etki ve Örgütsel Politika (`influence.py`):** NetworkX destekli PageRank, betweenness centrality, gizli koalisyonlar, bilgi bekçileri (gatekeepers) ve kilit aracılar (brokers).
- **İlişki Entropisi (`entropy.py`):** Shannon entropisi, güven dalgalanması (volatilite) ve etkileşim düzenliliği ile öngörülemezlik ölçümü.
- **Birleşik Risk Analizi (`risk.py`):** Eyleme geçirilebilir faktörler ve taktiksel öneriler içeren paydaş risk puanları.

### 2. ⚡ Canlı Yapay Zeka Stratejik Danışmanı (Tactical Briefing)
- Herhangi bir paydaşın sayfasında veya MCP üzerinden (`generate_tactical_briefing`) toplantı öncesi taktiksel müzakere savaş planı üretir.
- Desteklenen yapay zekâ motorları:
  - 🟢 **Dahili Taktiksel Motor (Çevrimdışı / Anında):** Kapsamlı sezgisel kurallar ve psikometrik analiz.
  - ✨ **Google Gemini:** `gemini-2.0-flash`, `gemini-1.5-pro`
  - 🧠 **OpenAI:** `gpt-4o-mini`, `gpt-4o`, `o3-mini`
  - ⚡ **Anthropic Claude:** `claude-3-5-sonnet-20241022`

### 3. 💾 Kalıcı Veri & Yazma API'leri
- Gerçek zamanlı JSON kalıcılığı (`data/crm_state.json`).
- `POST /api/interaction` — Toplantı, telefon, müzakere, iyilik veya çatışmaları güven güncellemeleriyle kaydeder.
- `POST /api/stakeholder` — Yeni paydaşları dinamik olarak ekler.
- `POST /api/reset` — Veri setini başlangıç senaryosuna sıfırlar.

### 4. 🔌 Dinamik Port Yönetimi
- Varsayılan olarak `5088` portunda başlar; port kullanımda ise otomatik olarak bir sonraki boş porta (`5089`, `5090`...) geçer.

---

## 🛠️ Hızlı Başlangıç

### 1. Repoyu Klonlayın ve Bağımlılıkları Yükleyin
```bash
git clone https://github.com/adacreativeco/strategic-memory-crm.git
cd strategic-memory-crm
pip install -r requirements.txt
```

### 2. Web Kontrol Panelini Başlatın
```bash
python app.py
```
Tarayıcınızda [http://localhost:5088](http://localhost:5088) adresini açın.

### 3. MCP Sunucusunu Başlatın (Stdio)
```bash
python mcp_server.py
```

### 4. Birim Testleri Çalıştırın
```bash
python -m unittest discover tests
```

---

## 📂 Mimari

```
strategic-memory-crm/
├── app.py                          # Flask web kontrol paneli & REST API'leri
├── mcp_server.py                   # Model Context Protocol (MCP) sunucu giriş noktası
├── strategic_memory_crm/
│   ├── models.py                   # Veri sınıfları (Stakeholder, Interaction, Relationship, CRMState)
│   ├── storage.py                  # JSON yükleme & kaydetme motoru
│   ├── trust.py                    # Güven dinamikleri & zamansal sönümleme motoru
│   ├── negotiation.py              # Davranışsal profilleme & kalıp tespiti
│   ├── influence.py                # Çizge merkeziliği, bilgi bekçileri, aracılar & koalisyonlar
│   ├── entropy.py                  # Shannon entropisi & ilişki dalgalanması
│   ├── risk.py                     # Birleşik risk analizi & öneriler
│   ├── mcp_tools.py                # Modüler MCP davranışsal zeka araçları
│   ├── graph.py                    # Vis.js JSON çizge serileştirme
│   ├── simulation.py               # Etkileşim geçmişi simülatörü
│   └── dataset.py                  # Örnek şirket birleşmesi (M&A) veri seti üreticisi
├── templates/                      # Jinja2 HTML şablonları
│   ├── base.html                   # Koyu temalı ana düzen
│   ├── dashboard.html              # Matris, istatistikler & etkileşim/paydaş modalları
│   ├── stakeholder.html            # Paydaş profili, zaman çizelgesi & AI Danışmanı
│   └── graph.html                  # Etkileşimli Vis.js ağ grafiği
├── static/
│   └── style.css                   # Duyarlı koyu UI tasarımı
├── tests/
│   ├── test_crm.py                 # Temel CRM birim test paketi
│   └── test_mcp.py                 # MCP sunucu ve araçları test paketi
├── data/                           # Kalıcı durum dizini (crm_state.json)
└── requirements.txt                # Bağımlılıklar (Flask, NetworkX, NumPy, SciPy, MCP)
```

---

## 📄 Lisans

Apache 2.0 Lisansı ile dağıtılmaktadır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

---

<div align="center">
🧠 <a href="https://github.com/adacreativeco">ADA Creative Co.</a> tarafından geliştirilmiştir.
</div>
