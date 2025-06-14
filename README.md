# FarmVille
<img width="821" alt="Screenshot 2025-05-24 at 10 04 25" src="https://github.com/user-attachments/assets/aee627a1-a994-4a9f-9e59-3ff560c8052b" />

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- **Docker**
- **Git**

### API Keys Required

You'll need to obtain the following API keys:

1. **OpenWeatherMap API Key**
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key

2. **OpenAI API Key**
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Get your API key (requires payment setup)

## Quick Start

### 1. Clone the Repository

```bash
git clone 
cd farmville
```

#### Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

#### Environment Configuration
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=farmville
POSTGRES_PASSWORD=farmville
POSTGRES_DB=farmville

# Authentication
JWT_SECRET=your-super-secret-jwt-key-here

# API Keys
OPENAI_API_KEY=your-openai-api-key-here
OPENWEATHERMAP_API_KEY=your-openweather-api-key-here
```

#### Docker setup

```bash
docker-compose up -d # OR make docker
```

#### Start Backend Server

```bash
python api_gateway.py # OR make run
```

The backend will be available at `http://localhost:5001`

## Testing

Run the test suite to ensure everything is working:

```bash
# Run all tests
python -m pytest tests/ -v # OR make test

# Run specific test file
python -m pytest tests/test_weather_service.py -v
```

## Project Structure

```
farmville/
├── api/                    # API route modules
│   ├── routes/
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── weather_routes.py   # Weather data endpoints
│   │   ├── agro_routes.py      # Agricultural analysis endpoints
│   │   ├── terrain_routes.py   # Terrain management endpoints
│   │   └── system_routes.py    # System health endpoints
│   └── __init__.py
├── services/               # Business logic services
│   ├── user_service.py         # User management
│   ├── weather_service.py      # Weather data handling
│   ├── agro_service.py         # AI agricultural analysis
│   ├── terrain_service.py      # Terrain operations
│   └── websocket_service.py    # Real-time updates
├── models/                 # Data models
│   ├── user.py                 # User model
│   ├── weather_data.py         # Weather data model
│   ├── agro_data.py            # Agricultural suggestion model
│   └── terrain.py              # Terrain model
├── database/               # Database layer
│   ├── connection.py           # Database connection
│   ├── user_repository.py      # User data access
│   └── terrain_repository.py   # Terrain data access
├── utils/                  # Utility modules
│   ├── patterns/               # Design patterns
│   └── observers/              # Observer implementations
├── tests/                  # Unit tests
├── api_gateway.py          # Main Flask application
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # PostgreSQL container setup
├── Makefile               # Development commands
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```