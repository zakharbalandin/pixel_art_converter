# Pixel Art Converter

A web application that converts regular images into pixel art style with various color palettes.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)

## Features

- 🎨 **Multiple Color Palettes**: GameBoy, NES, Grayscale, Retro, and Original
- 📏 **Adjustable Pixel Size**: Fine-tune the pixelation level (2-32px)
- 🖼️ **Supports Multiple Formats**: PNG, JPG, GIF, WebP, BMP
- 👤 **User Authentication**: Register, login, and track conversion history
- 📊 **Conversion Statistics**: Track processing time and file sizes
- 💾 **PostgreSQL Database**: Persistent storage for users and history
- 📝 **Comprehensive Logging**: Structured logging for debugging

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/zakharbalandin/pixel_art_converter.git
cd pixel_art_converter
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```bash
createdb pixel_art_db
```

5. Configure environment variables:
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pixel_art_db
export SECRET_KEY=your-secret-key-here
```

6. Run the application:
```bash
python app.py
```

7. Open http://localhost:5000 in your browser

### Using Docker

```bash
docker-compose up -d
```

## Project Structure

```
pixel_art_converter/
├── app.py              # Flask application
├── converter.py        # Image conversion logic
├── models.py           # Database models
├── logging_config.py   # Logging configuration
├── requirements.txt    # Python dependencies
├── pytest.ini          # Pytest configuration
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── history.html
│   └── error.html
├── tests/              # Test suite
│   ├── conftest.py
│   ├── test_converter.py
│   └── test_app.py
└── .github/
    └── workflows/
        └── ci.yml      # CI/CD pipeline
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with converter interface |
| `/convert` | POST | Convert an image |
| `/result/<filename>` | GET | Get converted image |
| `/download/<filename>` | GET | Download converted image |
| `/register` | GET/POST | User registration |
| `/login` | GET/POST | User login |
| `/logout` | GET | User logout |
| `/history` | GET | View conversion history |
| `/api/palettes` | GET | Get available palettes |
| `/api/stats` | GET | Get conversion statistics |

## Available Palettes

- **GameBoy**: Classic 4-color green palette
- **NES**: Nintendo Entertainment System colors
- **Grayscale**: 8 shades of gray
- **Retro**: C64-inspired 16 colors
- **Original**: Keep original colors (pixelation only)

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_converter.py -v
```

## Development

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://postgres:postgres@localhost:5432/pixel_art_db` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `LOG_LEVEL` | Logging level | `INFO` |

