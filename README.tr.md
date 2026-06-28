# Strategic Memory CRM

🇺🇸 [English Documentation](README.md)

> İşlem depolama yerine ilişki zekası.

Anlaşma ve pipeline takibi yerine **davranışsal zeka** modelleyen hafif bir CRM prototipi — güven dinamikleri, müzakere kalıpları, etki yapıları, organizasyonel politika ve ilişki riski.

Stratejistler, operasyon yöneticileri ve *kimin kime güvendiğinin*, *kimin ne satın aldığından* daha önemli olduğu karmaşık paydaş ekosistemlerinde yol alan herkes için tasarlandı.

---

## Ne Modelliyor

### Güven Dinamikleri
Güven asimetriktir, süreklidir ve zamana bağlıdır. Etkileşim geçmişi, taahhüt tutma, karşılıklılık dengesi ve kişilik uyumu üzerinden evrilir. İlişkiler hareketsiz kaldığında güven pasif olarak nötre (0.5) doğru çürür.

### Müzakere Kalıpları
Paydaşlar müzakere davranışlarına göre profillenir — baskıcı, uzlaştırıcı, işbirlikçi, rekabetçi veya kaçınmacı. Sistem seri söz kıranları, kronik taviz verenleri, saf tırmandırıcıları ve çiftler arası karşılıklı dinamikleri tespit eder.

### Etki Yapıları
Resmi hiyerarşi ile gayri resmi güç ağları bir arada. PageRank, arasındalık merkeziliği (betweenness centrality) ve yakınlık merkeziliği (closeness centrality) bilgi akışını gerçekte kimin kontrol ettiğini belirler. Koalisyon tespiti gizli ittifakları ortaya çıkarır; eklemlenme noktası analizi ağı bir arada tutan aracıları (broker) bulur.

### Organizasyonel Politika
Politik zafiyet puanlaması; rakipleri tarafından geçilen, müttefik eksikliği yaşayan, tek bir ilişkiye bağımlı olan veya ağda izole kalan paydaşları işaretler. Güç puanları, yapısal merkeziliği organizasyonel kademe ve güven ağırlıklı gelen bağlantılarla harmanlar.

### İlişki Entropisi
İlişki öngörülemezliğinin bilgi-kuramsal ölçümü. Duygu geçmişi üzerinden Shannon entropisi, güven delta oynaklığı ve etkileşim düzenliliğini birleştirir. Yüksek entropi = değişken ve okunması zor. Düşük entropi = kararlı ve öngörülebilir (iyi ya da kötü).

### İlişki Riski
Güven eğilimi, entropi, karşılıklılık dengesizliği, politik zafiyet ve bağımlılık yoğunlaşmasını birleştiren bileşik risk değerlendirmesi. Her paydaş için eyleme dönüştürülebilir risk faktörleri ve öneriler üretilir.

---

## Senaryo

Dahil edilen veri seti, Meridian Systems (satın alan) ile Vantage Analytics (hedef) arasında bir **teknoloji şirketi satın almasını** simüle eder. On iki paydaş her iki organizasyonda C-suite, VP, direktör, yönetici ve dış danışman rollerini kapsar:

| Paydaş | Rol | Organizasyon |
|---|---|---|
| Diana Kessler | CEO | Meridian Systems |
| Robert Tanaka | CFO | Meridian Systems |
| Samira Okafor | Mühendislik VP'si | Meridian Systems |
| Marcus Webb | Ürün Direktörü | Meridian Systems |
| Linda Chen | Operasyon Direktörü | Meridian Systems |
| James Holloway | CEO (ayrılan) | Vantage Analytics |
| Priya Sharma | CFO | Vantage Analytics |
| Elena Vasquez | Ürün VP'si | Vantage Analytics |
| Tomás Rivera | Mühendislik Lideri | Vantage Analytics |
| Aisha Mbeki | Veri Bilimi Yöneticisi | Vantage Analytics |
| Catherine Blackwood | M&A Danışmanı | Blackwood & Associates |
| Philip Raines | Yönetim Kurulu Üyesi | Meridian Board |

6 ay boyunca 80 etkileşim simüle edilir — toplantılar, müzakereler, çatışmalar, iyilikler, ihanetler, işbirlikleri — gerçekçi duygu dinamikleri, taahhüt takibi, bilgi akışı ve güç hamleleriyle birlikte.

---

## Hızlı Başlangıç

```bash
# Klonla
git clone https://github.com/adacreativeco/strategic-memory-crm.git
cd strategic-memory-crm

# Bağımlılıkları kur
pip install -r requirements.txt

# Dashboard'u çalıştır
python app.py
```

Tarayıcıda [http://localhost:5000](http://localhost:5000) adresini aç.

---

## Mimari

```
strategic-memory-crm/
├── app.py                          # Flask web dashboard
├── strategic_memory_crm/
│   ├── models.py                   # Temel veri modelleri
│   ├── trust.py                    # Güven dinamikleri motoru
│   ├── negotiation.py              # Müzakere kalıbı analizi
│   ├── influence.py                # Etki & organizasyonel politika
│   ├── entropy.py                  # İlişki entropi puanlaması
│   ├── risk.py                     # Bileşik risk değerlendirmesi
│   ├── graph.py                    # Paydaş grafik oluşturucu
│   ├── simulation.py               # Etkileşim geçmişi simülatörü
│   └── dataset.py                  # Kurgusal veri seti üretici
├── templates/                      # Jinja2 HTML şablonları
│   ├── base.html
│   ├── dashboard.html
│   ├── stakeholder.html
│   └── graph.html
├── static/
│   └── style.css                   # Koyu temalı minimal arayüz
├── data/generated/                 # Üretilmiş JSON veri setleri
└── requirements.txt
```

### Modüller

| Modül | Amaç |
|---|---|
| `models.py` | Stakeholder, Interaction, Relationship ve CRMState veri sınıfları |
| `trust.py` | Çürüme, taahhüt takibi, karşılıklılık, kişilik uyumu ile güven puanlaması |
| `negotiation.py` | Davranışsal profilleme (stil sınıflandırması, kalıp tespiti, karşılıklı çift analizi) |
| `influence.py` | NetworkX destekli merkezilik metrikleri, kapıcı/aracı tespiti, koalisyon bulma, güç puanlaması |
| `entropy.py` | Duygular üzerinden Shannon entropisi, güven oynaklığı, etkileşim düzenliliği, bileşik puanlama |
| `risk.py` | İlişki başına ve paydaş başına risk, faktörler ve öneriler |
| `graph.py` | Ön yüz kuvvet yönlü görselleştirme için JSON grafik serileştirmesi |
| `simulation.py` | Kişilik odaklı dinamiklerle ağırlıklı rastgele etkileşim üretici |
| `dataset.py` | Tam senaryo oluşturucu (paydaşlar + simülasyon + puanlama + JSON dışa aktarım) |

---

## Dashboard

Web arayüzü üç görünüm sunar:

### Arayüz Önizlemesi

#### İlişki Zekası Paneli
![İlişki Zekası Paneli](dashboard_screenshot.png)

#### Paydaş Detayı Görünümü
![Paydaş Detay Görünümü](stakeholder_screenshot.png)

#### Paydaş Ağ Grafiği
![Ağ Grafiği Görünümü](graph_screenshot.png)

### İlişki Zekası Paneli (`/`)
- Ağ düzeyinde istatistikler: paydaş sayısı, etkileşim sayısı, aktif ilişkiler, ağ entropisi
- Ağ zekası: tespit edilen kapıcılar, aracılar, koalisyonlar ve karşılıklı müzakere dinamikleri
- Güven, güç, risk puanları, müzakere stilleri ve zafiyet bayraklarıyla paydaş risk matrisi

### Paydaş Detayı (`/stakeholder/<id>`)
- Etki metrikleri (güç puanı, PageRank, arasındalık merkeziliği)
- Faktörler ve eyleme dönüştürülebilir önerilerle risk değerlendirmesi
- Kişilik profili görselleştirmesi
- Müzakere profili (stil, güvenilirlik, taviz oranı, kalıplar)
- Güven, entropi, risk, eğilim ile ilişki tablosu
- Duygu renklendirmesi, taahhüt takibi, bilgi akışı ile etkileşim zaman çizelgesi

### Paydaş Ağ Grafiği (`/graph`)
- Sürükle, kaydır, yakınlaştır özellikli kuvvet yönlü grafik
- Düğüm boyutu = etki (PageRank), düğüm rengi = organizasyon
- Kenar rengi = güven seviyesi (yeşil/turuncu/kırmızı), kenar kalınlığı = etkileşim sıklığı
- İpuçları için üzerine gel, paydaş detayına gitmek için çift tıkla

---

## API Uç Noktaları

Tüm veriler programatik erişim için JSON olarak mevcuttur:

| Uç Nokta | Açıklama |
|---|---|
| `GET /api/state` | Tam CRM durumu (paydaşlar, etkileşimler, ilişkiler) |
| `GET /api/graph` | Görselleştirme için grafik verisi (düğümler + kenarlar) |
| `GET /api/entropy` | Ağ entropisi + ilişki başına entropi dağılımları |
| `GET /api/influence` | Merkezilik metrikleri, kapıcılar, aracılar, koalisyonlar, güç puanları |
| `GET /api/risk` | Paydaş başına risk değerlendirmeleri, faktörler ve öneriler |
| `GET /api/negotiations` | Tüm paydaşlar için müzakere profilleri |

---

## Kavramlar

### Güven Puanı (0–1)
Sürekli, asimetrik. Etkileşim duygusu, taahhüt tutma, karşılıklılık, kişilik uyumu ve açık güven deltaları ile güncellenir. Zamanla pasif olarak 0.5'e (nötr) doğru çürür.

### İlişki Entropisi (0–1)
Bileşenleri:
- **Duygu entropisi** (0.45 ağırlık): Ayrıklaştırılmış duygu gözlemleri üzerinden Shannon entropisi
- **Güven oynaklığı** (0.35 ağırlık): Güven deltalarının standart sapması
- **Etkileşim düzenliliği** (0.20 ağırlık): Etkileşimler arası zamanlama varyasyon katsayısı

### Güç Puanı
Ağırlıklı karışım:
- **PageRank** (0.40): Yönlü güven ağırlıklı graftaki yapısal etki
- **Organizasyonel kademe** (0.30): Resmi hiyerarşi pozisyonu
- **Gelen güven** (0.30): Diğer paydaşlardan gelen ortalama güven puanı

### Müzakere Stilleri
- **Baskıcı (Dominator)**: Sık güç hamleleri, nadiren taviz verir
- **Uzlaştırıcı (Accommodator)**: Sık taviz verir, çatışmadan kaçınır
- **İşbirlikçi (Collaborator)**: Dengeli alışveriş, yüksek güvenilirlik
- **Rekabetçi (Competitor)**: Avantaj için zorlar, orta düzey tavizler
- **Kaçınmacı (Avoider)**: Müzakereye düşük katılım

---

## Tasarım Felsefesi

Bu prototip bilinçli olarak kurumsal CRM karmaşıklığından (pipeline'lar, lead puanlaması, e-posta entegrasyonu, Salesforce-tarzı iş akışları) kaçınır. Bunun yerine odaklanır:

1. **İşlemsel veri yerine davranışsal sinyal** — Birinin ilişkilerde *ne yaptığı*, *ne satın aldığından* daha fazlasını ortaya koyar.
2. **Sistem düşüncesi** — İlişkiler ağlarda var olur. Bir paydaşın riski sadece doğrudan bağlantılarına değil, tüm grafa bağlıdır.
3. **Birinci sınıf metrik olarak entropi** — Öngörülemezlik, başlı başına ölçülmeye değer bir risk sinyalidir.
4. **Asimetrik güven** — A'nın B'ye güveni ≠ B'nin A'ya güveni. Bu asimetriyi modellemek gerçek dünya güç dinamiklerini yakalar.
5. **Politik zeka** — Resmi hiyerarşi hikayenin yarısını anlatır. Gayri resmi etki, koalisyon dinamikleri ve aracılık geri kalanını anlatır.

---

## Teknoloji Yığını

- **Python 3.10+**
- **Flask** — Minimal web çatısı
- **NetworkX** — Grafik algoritmaları (PageRank, arasındalık, topluluk tespiti)
- **NumPy/SciPy** — Sayısal hesaplama
- **Vanilla JS + Canvas** — Kuvvet yönlü grafik görselleştirme (ağır frontend çatısı yok)

---

## Lisans

Apache Lisansı 2.0 - Telif Hakkı 2026 Ada Creative Co. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.
