# GPS Tracker API - Docker Deployment

## Hızlı Başlangıç

### Ön Koşullar
- Docker
- Docker Compose

### Kurulum ve Çalıştırma

1. **Environment dosyasını oluştur** (isteğe bağlı):
```bash
cp .env.example .env
# İsterseniz .env dosyasını düzenleyebilirsiniz
```

2. **Docker Compose ile başlat**:
```bash
docker-compose up -d
```

3. **API'ye erişim**:
- Swagger UI (API Documentation): http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- ReDoc (Alternative Docs): http://localhost:8000/redoc

### Durumu Kontrol Et
```bash
docker-compose ps
```

### Logları Görüntüle
```bash
docker-compose logs -f api        # API logları
docker-compose logs -f postgres   # Database logları
docker-compose logs -f            # Tüm loglar
```

### Durdur
```bash
docker-compose down
```

## Detaylı Açıklama

### docker-compose.yml Yapısı

**PostgreSQL Servisi:**
- Image: `postgres:16-alpine` (küçük ve hızlı)
- Port: `5432` (lokal erişim için)
- Volume: `postgres_data` (veri kalıcılığı)
- Health check: Otomatik başlatma ve yeniden bağlantı

**API Servisi:**
- Build: Local Dockerfile'dan oluşturulur
- Environment: Database URL otomatik olarak ayarlanır
- Port: `8000` (lokal ve dış erişim)
- Depends on: Postgres sağlıklı olana kadar beklenir
- Restart: Container çökmesi halinde otomatik yeniden başlatılır
- **Pure REST API** - Frontend uygulamalar bu API'ye bağlanacak

### Environment Variables

`.env` dosyasında şu değişkenleri ayarlayabilirsiniz:

```env
DB_USER=postgres              # PostgreSQL kullanıcısı
DB_PASSWORD=your_password     # PostgreSQL şifresi
DB_NAME=gps                   # Database adı
```

Dockerfile otomatik olarak `DATABASE_URL` oluşturur.

## Production Deployment

### VDS'de Çalıştırma

1. **Repoyu klonla:**
```bash
git clone <repo-url> /opt/gps_tracker
cd /opt/gps_tracker
```

2. **.env dosyasını güvenli şekilde oluştur:**
```bash
cat > .env << EOF
DB_USER=postgres
DB_PASSWORD=$(openssl rand -base64 32)
DB_NAME=gps
EOF
chmod 600 .env
```

3. **Docker volumes ve ağını oluştur:**
```bash
docker network create gps_network
docker volume create gps_postgres_data
```

4. **Production modunda çalıştır:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

5. **Nginx ile proxy kur** (isteğe bağlı):
```nginx
upstream gps_api {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://gps_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /ws {
        proxy_pass http://gps_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup ve Restore

### Database Backup
```bash
docker-compose exec postgres pg_dump -U postgres gps > backup.sql
```

### Database Restore
```bash
docker-compose exec -T postgres psql -U postgres gps < backup.sql
```

## Sorun Giderme

### API bağlanamıyor
```bash
# Logları kontrol et
docker-compose logs api

# Container'ı yeniden başlat
docker-compose restart api
```

### Database bağlantı hatası
```bash
# Database container'ı kontrol et
docker-compose logs postgres

# Database sağlıklı mı kontrol et
docker-compose exec postgres pg_isready -U postgres
```

### Port zaten kullanımda
```bash
# docker-compose.yml dosyasında port numarasını değiştir
# veya:
docker-compose down && docker-compose up -d
```

## Otomatik Yeniden Başlatma

Sunucu yeniden başladığında container'ları otomatik olarak başlatmak için:

```bash
# Tüm container'ları restart policy ile ayarla
docker update --restart=always gps_tracker_api
docker update --restart=always gps_tracker_db
```

## Performance Tips

1. **Memory limit ayarla** (docker-compose.yml):
```yaml
services:
  api:
    mem_limit: 512m
  postgres:
    mem_limit: 1g
```

2. **CPU limit ayarla**:
```yaml
services:
  api:
    cpus: '1'
```

3. **Log rotation ayarla**:
```bash
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 ...
```

## Monitoring

```bash
# Real-time resource usage
docker stats

# Container inspect
docker inspect gps_tracker_api

# Network inspect
docker network inspect gps_network
```

## Frontend Applications

Bu API'ye bağlanacak frontend uygulamalar (web, mobile) ayrı repolarda tutulacaktır:

### API Endpoints

**REST Endpoints:**
- `POST /api/device` - Yeni cihaz oluştur
- `GET /api/devices` - Tüm cihazları listele
- `GET /api/device/{device_id}/tracks` - Cihazın GPS kayıtlarını al
- `GET /api/export/gpx/{device_id}` - GPX dosyası indir

**WebSocket:**
- `WebSocket /ws/{device_id}` - Gerçek-zamanlı GPS verisi
  - `device_id=0`: Dinleme modu (harita viewer)
  - `device_id>0`: Veri gönderme modu (tracker)

### Example Client Connection

```javascript
// WebSocket bağlantısı
const ws = new WebSocket('ws://localhost:8000/ws/1');

ws.onopen = () => {
  console.log('Connected');
  // GPS verisi gönder
  ws.send(JSON.stringify({
    latitude: 41.0082,
    longitude: 28.9784,
    accuracy: 5.2
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Location update:', data);
};
```

### CORS Configuration

API tüm originlere izin verecek şekilde yapılandırılmıştır (`allow_origins=["*"]`). Production'da kısıtlayabilirsiniz (`src/app.py` dosyasında CORS middleware ayarlarını değiştirin).
