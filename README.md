# GPS Tracker API 📍

Pure REST API + WebSocket tabanlı gerçek zamanlı GPS izleme sistemi.
Frontend uygulamalar (web, mobile) bu API'ye bağlanacak.

## Özellikler

- ✅ REST API endpoints
- ✅ WebSocket ile gerçek zamanlı konum akışı
- ✅ PostgreSQL veritabanı
- ✅ GPX export (Google Earth, Strava vb. ile uyumlu)
- ✅ Birden fazla cihaz (device) desteği
- ✅ Docker + Docker Compose ile deployment
- ✅ Pydantic BaseSettings ile konfigürasyon
- ✅ SQLAlchemy ORM + Repository Pattern

## Hızlı Başlangıç

### Gereksinimler
- Python 3.12+
- PostgreSQL 16 (veya Docker)
- Git

### Lokal Çalıştırma

```bash
# 1. Repoyu klonla
git clone <repo_url>
cd gps_tracker

# 2. Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# VEYA
venv\Scripts\activate  # Windows

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. .env ayarla (gerekirse)
cp .env.example .env

# 5. API'yi çalıştır
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

API Docs: http://localhost:8000/docs

### Docker ile Çalıştırma

```bash
docker-compose up -d
```

Bkz. `DOCKER.md` detaylar için.

## API Endpoints

### REST Endpoints

| Metod | Endpoint | Açıklama |
|-------|----------|----------|
| POST | `/api/device?name=X&color=Y` | Yeni cihaz oluştur |
| GET | `/api/devices` | Tüm cihazları listele |
| GET | `/api/device/{device_id}/tracks` | Cihazın GPS kayıtlarını al |
| GET | `/api/export/gpx/{device_id}` | GPX dosyası indir |

### WebSocket

| Endpoint | Açıklama |
|----------|----------|
| `ws://localhost:8000/ws/{device_id}` | Gerçek-zamanlı GPS verisi (device_id=0: dinleme, device_id>0: gönderme) |

### Örnek İstekler

```bash
# Cihaz oluştur
curl -X POST "http://localhost:8000/api/device?name=Araç-1&color=%23FF0000"

# Cihazları listele
curl "http://localhost:8000/api/devices"

# GPS kayıtlarını al
curl "http://localhost:8000/api/device/1/tracks"

# GPX indir
curl "http://localhost:8000/api/export/gpx/1" -o device.gpx
```

### WebSocket Kullanımı

JavaScript örneği:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/1');

ws.onopen = () => {
  ws.send(JSON.stringify({
    latitude: 41.0082,
    longitude: 28.9784,
    accuracy: 5.2
  }));
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Location:', update);
};
```

## Proje Yapısı

```
gps_tracker/
├── src/
│   ├── app.py                 # FastAPI app
│   ├── config.py              # Pydantic BaseSettings
│   ├── datalayer/
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── model/db/
│   │   │   ├── device.py
│   │   │   └── gps_track.py
│   │   └── repository/
│   │       ├── _base_repository.py
│   │       ├── device_repository.py
│   │       └── gps_track_repository.py
│   ├── routes/
│   │   ├── device_routes.py
│   │   └── track_routes.py
│   └── utils/
│       └── websocket_manager.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Deployment

Docker ile production deployment için:

```bash
docker-compose up -d
```

Bkz. `DOCKER.md` detayları için.

## Frontend Uygulamalar

Bu API'ye bağlanacak ayrı repolarda geliştirilecek:
- **Web Frontend** (React/Vue/Next.js)
- **Mobile App** (React Native/Flutter)

## Lisans

MIT
