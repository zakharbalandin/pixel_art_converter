# Pixel Art Converter

A Flask web application that converts images to pixel art style with various color palettes.

## Features

- Convert images to pixel art with configurable pixel size (1-64)
- Multiple color palettes: gameboy, nes, grayscale, retro, original
- User authentication and conversion history
- RESTful API endpoints
- **Full monitoring stack with Prometheus, Loki, and Grafana**

## Quick Start

### With Docker Compose (Recommended)

```bash
# Start all services including monitoring
docker-compose up -d

# View logs
docker-compose logs -f web
```

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Web App | http://localhost:5000 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Loki | http://localhost:3100 | - |

## Monitoring Stack

### Prometheus (Metrics)

Collects application metrics from the `/metrics` endpoint:

- `flask_http_request_total` - Total HTTP requests
- `flask_http_request_duration_seconds` - Request latency histogram
- `conversions_total` - Total image conversions by palette
- `conversion_duration_seconds` - Conversion processing time

### Loki (Logs)

Collects JSON-formatted application logs via Promtail:

- All application actions are logged with structured JSON
- Logs include: action type, user_id, timestamps, request details
- Labels: service, level, action

### Grafana (Visualization)

Pre-configured dashboard includes:

- Total conversions counter
- Request rate graph
- P95 response time
- Error rate (5xx)
- Request rate by endpoint
- Conversion duration by palette
- Live application logs
- Logs by level chart

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main converter interface |
| `/convert` | POST | Convert image to pixel art |
| `/result/<filename>` | GET | Get converted image |
| `/download/<filename>` | GET | Download converted image |
| `/api/palettes` | GET | List available palettes |
| `/api/stats` | GET | Get conversion statistics |
| `/metrics` | GET | Prometheus metrics |
| `/health` | GET | Health check endpoint |

## Color Palettes

- **gameboy**: Classic Game Boy green palette (4 colors)
- **nes**: Nintendo Entertainment System palette (24 colors)
- **grayscale**: 8 shades of gray
- **retro**: Classic computer colors (16 colors)
- **original**: Keep original colors (pixelation only)

## Development

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=sqlite:///dev.db
export SECRET_KEY=dev-secret-key

# Run application
python app.py
```

### Running Tests

```bash
pytest -v --cov=.
```

## Logging

All application actions are logged in JSON format for Loki compatibility:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "app",
  "message": "Conversion completed",
  "service": "pixel-art-converter",
  "action": "convert_success",
  "conversion_id": 123,
  "processing_time_ms": 250
}
```

### Logged Actions

- `app_init` - Application startup
- `page_view` - Page access
- `convert_start/success/error` - Image conversion
- `login_attempt/success/failed` - Authentication
- `register_attempt/success/failed` - Registration
- `logout` - User logout
- `api_call` - API endpoint access
- `error_404/500/413` - HTTP errors

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | Database connection string |
| `SECRET_KEY` | dev-secret-key | Flask secret key |
| `LOG_LEVEL` | INFO | Logging level |

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Flask App  │────▶│  PostgreSQL │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           │ /metrics
                           ▼
                    ┌─────────────┐
                    │  Prometheus │
                    └─────────────┘
                           │
                           ▼
┌─────────────┐     ┌─────────────┐
│  Promtail   │────▶│    Loki     │
└─────────────┘     └─────────────┘
       │                   │
       │ (Docker logs)     │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│  Flask App  │     │   Grafana   │
│   (stdout)  │     │ (Dashboard) │
└─────────────┘     └─────────────┘
```

## License

MIT

---

## Ansible Deployment (Multi-VM)

For production deployment across multiple VMs, use the Ansible playbooks:

### Infrastructure

| Host | IP Address | Role |
|------|------------|------|
| server | 192.168.122.4 | Flask App + PostgreSQL |
| node1 | 192.168.122.5 | Monitoring Stack |
| node2 | 192.168.122.6 | Secondary Flask App |

### Quick Start

```bash
# Install Ansible collections
cd ansible/
ansible-galaxy install -r requirements.yml

# Test connectivity
ansible all -m ping

# Deploy everything
ansible-playbook playbook.yml
```

### Access Points (After Deployment)

| Service | URL |
|---------|-----|
| Web App (Primary) | http://192.168.122.4:5000 |
| Web App (Secondary) | http://192.168.122.6:5000 |
| Grafana | http://192.168.122.5:3000 |
| Prometheus | http://192.168.122.5:9090 |

See `ansible/README.md` for detailed documentation.
