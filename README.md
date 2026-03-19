# GPS Tracker 📍

WebSocket tabanlı gerçek zamanlı GPS izleme uygulaması. Telefondan GPS konumunu gönder, masaüstünde canlı haritada izle.

## Özellikler

- ✅ WebSocket ile gerçek zamanlı konum güncelleme
- ✅ Leaflet + OpenStreetMap harita
- ✅ Birden fazla telefon (device) desteği
- ✅ PostgreSQL veritabanı
- ✅ GPX export (Google Earth, Strava vb. ile uyumlu)
- ✅ Konum doğruluğu, hız, süre takibi
- ✅ Otomatik yeniden bağlantı

## Kurulum

### Gereksinimler
- Python 3.8+
- PostgreSQL 12+
- Git

### Adımlar

1. **Repoyu klonla**
```bash
git clone <repo_url>
cd gps_tracker
```

2. **Virtual environment oluştur**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# VEYA
venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları yükle**
```bash
pip install -r requirements.txt
```

4. **`.env` dosyasını ayarla**
```bash
# .env dosyası zaten hazırlanmış:
DATABASE_URL=postgresql://postgres:12.34.qw.er.@45.88.137.131:5432/gps
```

5. **Sunucuyu başlat**
```bash
uvicorn main:app --reload
```

Tarayıcıda aç:
- **Masaüstü (Harita):** http://localhost:8000/
- **Telefon (GPS Gönderici):** http://localhost:8000/track

## Kullanım

### Telefonda
1. `http://localhost:8000/track` adresine git
2. Cihaz adı gir (ör: "Araç-1")
3. **BAŞLAT** butonuna bas
4. GPS izni ver
5. Konum gönderisi başlar

### Masaüstünde
1. `http://localhost:8000/` adresine git
2. Canlı haritada rotalı görürsün
3. Renklendirme her cihaz için benzersiz
4. **GPX** butonuyla dosya indir

## API Endpoints

| Metod | Endpoint | Açıklama |
|-------|----------|----------|
| GET | `/` | Harita ekranı (HTML) |
| GET | `/track` | Telefon ekranı (HTML) |
| POST | `/api/device?name=X&color=Y` | Yeni cihaz oluştur |
| GET | `/api/devices` | Tüm cihazlar |
| GET | `/api/device/{id}/tracks` | Cihazın tüm konumları |
| GET | `/api/export/gpx/{id}` | GPX dosyası indir |
| WS | `/ws/{device_id}` | WebSocket (konum gönderimi) |

## Veritabanı Şeması

### `devices` tablosu
```sql
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### `gps_tracks` tablosu
```sql
CREATE TABLE gps_tracks (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    latitude FLOAT,
    longitude FLOAT,
    accuracy FLOAT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## Deployment (VDS)

Bkz. `DEPLOYMENT.md`

## Development

Dosya yapısı:
```
gps-tracker/
├── main.py              # FastAPI backend
├── tracker.html         # Telefon ekranı (GPS gönderici)
├── index.html           # Masaüstü harita ekranı
├── config.py            # Konfigürasyon
├── requirements.txt     # Python bağımlılıkları
├── .env                 # Çevre değişkenleri
└── .gitignore
```

## Lisans

MIT
