# Strategic Memory CRM

🇹🇷 Türkçe Dokümantasyon | 🇺🇸 [English Documentation](README.md)

> İşlem depolamak yerine ilişki ve davranış zekası yönetimi.

Yalnızca satış anlaşmalarını ve boru hatlarını (pipeline) tutmak yerine **güven dinamiklerini, müzakere modellerini, etki yapılarını, organizasyonel politikayı ve ilişki riskini** modelleyen davranışsal zeka CRM platformu.

Kimin kime güvendiğinin kimin ne satın aldığından daha önemli olduğu karmaşık paydaş ekosistemlerinde stratejistler ve liderler için tasarlanmıştır.

---

## 🚀 Öne Çıkan Özellikler

### 1. 🧠 Davranışsal Zeka Motoru
- **Güven Dinamikleri (`trust.py`):** Asimetrik güven puanlama, zamana bağlı sönümleme (passive decay), karşılıklılık dengesi ve kişilik uyumu.
- **Müzakere Profili (`negotiation.py`):** Dominant, işbirlikçi, taviz veren ve kaçınmacı stiller; sözünden dönenler (promise-breakers) ve kronik tavizcilerin tespiti.
- **Etki ve Örgütsel Politika (`influence.py`):** NetworkX destekli PageRank, betweenness centrality, gizli koalisyonlar, bilgi bekçileri (gatekeepers) ve kilit aracılar (brokers).
- **İlişki Entropisi (`entropy.py`):** Shannon entropisi, güven dalgalanması (volatilite) ve etkileşim düzenliliği ile öngörülemezlik ölçümü.
- **Birleşik Risk Analizi (`risk.py`):** Eyleme geçirilebilir faktörler ve taktiksel öneriler içeren paydaş risk puanları.

### 2. ⚡ Canlı Yapay Zeka Stratejik Danışmanı (Tactical Briefing)
- Herhangi bir paydaşın sayfasında toplantı öncesi taktiksel müzakere savaş planı üretimi (`POST /api/advisor/briefing`).
- Desteklenen yapay zeka motorları:
  - 🟢 **Dahili Taktiksel Motor (Çevrimdışı / Anında):** Sezgisel kurallar ve psikometrik analiz.
  - ✨ **Google Gemini:** `gemini-2.0-flash`, `gemini-1.5-pro`
  - 🧠 **OpenAI:** `gpt-4o-mini`, `gpt-4o`, `o3-mini`
  - ⚡ **Anthropic Claude:** `claude-3-5-sonnet-20241022`

### 3. 💾 Veri Kalıcılığı ve Yazma API'ları
- Gerçek zamanlı JSON dosya kalıcılığı (`data/crm_state.json`).
- `POST /api/interaction` — Toplantı, telefon, müzakere, jest veya çatışmaları anlık güven güncellemesiyle kaydetme.
- `POST /api/stakeholder` — Dinamik olarak yeni paydaşlar ekleme.
- `POST /api/reset` — Verileri başlangıç senaryosuna sıfırlama.

### 4. 🔌 Dinamik Port Çakışma Yönetimi
- Varsayılan olarak `5088` portunda başlar; port meşgulse otomatik olarak bir sonraki boş porta (`5089`, `5090`...) geçer.

---

## 🛠️ Kurulum ve Başlangıç

### 1. Bağımlılıkları Yükleyin
```bash
git clone https://github.com/adacreativeco/strategic-memory-crm.git
cd strategic-memory-crm
pip install -r requirements.txt
```

### 2. Dashboard'u Başlatın
```bash
python app.py
```
Tarayıcınızda [http://localhost:5088](http://localhost:5088) adresini açın.

### 3. Otomatik Testleri Çalıştırın
```bash
python -m unittest tests/test_crm.py
```

---

## 📂 Proje Mimarisi

```
strategic-memory-crm/
├── app.py                          # Flask web dashboard ve REST API'ları
├── strategic_memory_crm/
│   ├── models.py                   # Veri modelleri (Stakeholder, Interaction, Relationship, CRMState)
│   ├── storage.py                  # JSON kalıcılık motoru (load / save)
│   ├── trust.py                    # Güven dinamikleri ve sönümleme motoru
│   ├── negotiation.py              # Müzakere davranışı ve örüntü analizi
│   ├── influence.py                # Ağ merkezilikleri, bekçiler, aracılar ve koalisyonlar
│   ├── entropy.py                  # Shannon entropisi ve ilişki oynaklığı
│   ├── risk.py                     # Birleşik risk analizi ve öneriler
│   ├── graph.py                    # Vis.js JSON ağ serileştirmesi
│   ├── simulation.py               # Etkileşim geçmişi simülatörü
│   └── dataset.py                  # Örnek şirket birleşmesi veri seti üreticisi
├── templates/                      # Jinja2 HTML şablonları
│   ├── base.html                   # Koyu temalı ana düzen
│   ├── dashboard.html              # Risk matrisi, istatistikler ve etkileşim/paydaş modalları
│   ├── stakeholder.html            # Profil, zaman tüneli ve AI Stratejik Danışman
│   └── graph.html                  # Etkileşimli Vis.js ilişki ağı haritası
├── static/
│   └── style.css                   # Responsive koyu tema CSS stilleri
├── tests/
│   └── test_crm.py                 # Kapsamlı otomatik birim testleri (18 test)
├── data/                           # Kalıcı durum dizini (crm_state.json)
└── requirements.txt                # Bağımlılıklar (Flask, NetworkX, NumPy)
```

---

## 📄 Lisans

Apache 2.0 Lisansı kapsamında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.
