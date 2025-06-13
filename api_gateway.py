#!/usr/bin/env python3
"""
FarmVille API Gateway
Main Flask application
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Services
from services.user_service import UserService
from services.weather_service import WeatherService
from services.agro_service import AgroService
from services.terrain_service import TerrainService
from services.websocket_service import WebSocketService
from services.location_service import LocationService

# Routes
from api.routes import (
    auth_bp, 
    weather_bp, 
    agro_bp, 
    terrain_bp, 
    system_bp,
    location_bp
)

# Database
from database.connection import DatabaseConnection

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'your-secret-key')

# Enable CORS
CORS(app)

# Initialize database
db = DatabaseConnection()
if db.test_connection():
    print("✅ Database connected")
    db.update_existing_tables()
else:
    print("❌ Database connection failed")

# Initialize services
app.user_service = UserService()
app.weather_service = WeatherService()
app.location_service = LocationService()
app.terrain_service = TerrainService(location_service=app.location_service)
app.agro_service = AgroService()
app.websocket_service = WebSocketService()

print("🔧 Services initialized")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(agro_bp, url_prefix='/api/agro')
app.register_blueprint(terrain_bp, url_prefix='/api/terrains')
app.register_blueprint(location_bp, url_prefix='/api/location')
app.register_blueprint(system_bp, url_prefix='/api/system')

print("🔗 Routes registered")

@app.route('/')
def home():
    return jsonify({
        "service": "FarmVille API Gateway",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth",
            "weather": "/api/weather",
            "agro": "/api/agro", 
            "terrains": "/api/terrains",
            "location": "/api/location",
            "system": "/api/system"
        }
    })

if __name__ == '__main__':
    print("🚀 FarmVille API Gateway starting...")
    print("📍 Location service integrated")
    print("🌱 Enhanced terrain management")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )