"""
API Gateway for FarmVille
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from services.user_service import UserService
from services.terrain_service import TerrainService
from services.weather_service import WeatherService
from services.agro_service import AgroService
from services.websocket_service import WebSocketService, setup_websocket_handlers
from utils.observers.agro_observer import AgroAlertObserver, AgroLogObserver
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

user_service = UserService()
terrain_service = TerrainService()
weather_service = WeatherService()
agro_service = AgroService()

websocket_service = WebSocketService(socketio)

alert_observer = AgroAlertObserver()
log_observer = AgroLogObserver()

agro_service.attach(alert_observer)
agro_service.attach(log_observer)
agro_service.attach(websocket_service)

weather_service.attach(websocket_service)

setup_websocket_handlers(socketio, websocket_service)

def token_required(f):
    """Decorator for auth"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        user = user_service.get_user_from_token(token)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(user, *args, **kwargs)
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    
    result = user_service.register_user(
        data.get('username', ''),
        data.get('password', ''),
        data.get('email', '')
    )
    
    status = 201 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    
    result = user_service.login_user(
        data.get('username', ''),
        data.get('password', '')
    )
    
    status = 200 if result['success'] else 401
    return jsonify(result), status

@app.route('/api/auth/profile', methods=['GET'])
@token_required
def profile(current_user):
    """Get profile"""
    return jsonify({"user": current_user})

@app.route('/api/terrains', methods=['POST'])
@token_required
def create_terrain(current_user):
    """Criar novo terreno"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        result = terrain_service.create_terrain(
            user_id=current_user['id'],
            name=data.get('name', ''),
            latitude=float(data.get('latitude', 0)),
            longitude=float(data.get('longitude', 0)),
            crop_type=data.get('crop_type'),
            area_hectares=float(data['area_hectares']) if data.get('area_hectares') else None,
            notes=data.get('notes')
        )
        
        status = 201 if result['success'] else 400
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/terrains', methods=['GET'])
@token_required
def get_user_terrains(current_user):
    """Obter terrenos do utilizador"""
    try:
        result = terrain_service.get_user_terrains(current_user['id'])
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/terrains/<int:terrain_id>', methods=['GET'])
@token_required
def get_terrain(current_user, terrain_id):
    """Obter terreno específico"""
    try:
        result = terrain_service.get_terrain(terrain_id, current_user['id'])
        status = 200 if result['success'] else 404
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/terrains/<int:terrain_id>', methods=['PUT'])
@token_required
def update_terrain(current_user, terrain_id):
    """Atualizar terreno"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        # Preparar updates (apenas campos fornecidos)
        updates = {}
        
        if 'name' in data:
            updates['name'] = data['name']
        
        if 'latitude' in data:
            updates['latitude'] = float(data['latitude'])
        
        if 'longitude' in data:
            updates['longitude'] = float(data['longitude'])
        
        if 'crop_type' in data:
            updates['crop_type'] = data['crop_type']
        
        if 'area_hectares' in data:
            updates['area_hectares'] = float(data['area_hectares']) if data['area_hectares'] else None
        
        if 'notes' in data:
            updates['notes'] = data['notes']
        
        result = terrain_service.update_terrain(terrain_id, current_user['id'], **updates)
        status = 200 if result['success'] else 400
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/terrains/<int:terrain_id>', methods=['DELETE'])
@token_required
def delete_terrain(current_user, terrain_id):
    """Remover terreno"""
    try:
        result = terrain_service.delete_terrain(terrain_id, current_user['id'])
        status = 200 if result['success'] else 400
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/terrains/stats', methods=['GET'])
@token_required
def get_terrain_stats(current_user):
    """Obter estatísticas dos terrenos"""
    try:
        result = terrain_service.get_terrain_stats(current_user['id'])
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/terrains/<int:terrain_id>/weather', methods=['GET'])
@token_required
def get_terrain_weather(current_user, terrain_id):
    """Obter dados meteorológicos para um terreno específico"""
    try:
        # Obter terreno
        terrain_result = terrain_service.get_terrain(terrain_id, current_user['id'])
        
        if not terrain_result['success']:
            return jsonify(terrain_result), 404
        
        terrain = terrain_result['terrain']
        
        # Obter dados meteorológicos
        weather_data = weather_service.get_weather_data(
            terrain['name'], 
            terrain['latitude'], 
            terrain['longitude']
        )
        
        if weather_data:
            return jsonify({
                "success": True,
                "terrain": terrain,
                "weather": weather_data.to_dict()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not fetch weather data"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/terrains/<int:terrain_id>/agro-analysis', methods=['POST'])
@token_required
def get_terrain_agro_analysis(current_user, terrain_id):
    """Obter análise agrícola para um terreno específico"""
    try:
        # Obter terreno
        terrain_result = terrain_service.get_terrain(terrain_id, current_user['id'])
        
        if not terrain_result['success']:
            return jsonify(terrain_result), 404
        
        terrain = terrain_result['terrain']
        
        # Obter dados meteorológicos
        weather_data = weather_service.get_weather_data(
            terrain['name'], 
            terrain['latitude'], 
            terrain['longitude']
        )
        
        if not weather_data:
            return jsonify({
                "success": False,
                "error": "Could not fetch weather data"
            }), 500
        
        # Obter sugestões agrícolas
        suggestion = agro_service.analyze_weather_for_agriculture(weather_data)
        
        if suggestion:
            return jsonify({
                "success": True,
                "terrain": terrain,
                "weather": weather_data.to_dict(),
                "agro_suggestions": suggestion.to_dict()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not generate agricultural suggestions"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/weather/<location>', methods=['GET'])
@token_required
def get_weather(current_user, location):
    """Get weather for location"""
    try:
        lat = float(request.args.get('lat', 41.1579))
        lon = float(request.args.get('lon', -8.6291))
        
        weather_data = weather_service.get_weather_data(location, lat, lon)
        
        if weather_data:
            return jsonify({
                "success": True,
                "weather": weather_data.to_dict()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not fetch weather data"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/weather/bulk', methods=['POST'])
@token_required
def get_bulk_weather(current_user):
    """Get weather for multiple locations using threading"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        locations = data.get('locations', [])
        if not locations:
            return jsonify({"error": "No locations provided"}), 400
        
        location_tuples = [
            (loc.get('name', f"Location_{i}"), 
             float(loc.get('latitude', 0)), 
             float(loc.get('longitude', 0)))
            for i, loc in enumerate(locations)
        ]
        
        weather_data_list = weather_service.get_multiple_locations_concurrent(location_tuples)
        
        return jsonify({
            "success": True,
            "weather_data": [weather.to_dict() for weather in weather_data_list],
            "total_requested": len(locations),
            "total_fetched": len(weather_data_list)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/agro/analyze', methods=['POST'])
@token_required
def analyze_weather_for_agriculture(current_user):
    """Analyze weather data and get agricultural suggestions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        location = data.get('location', 'Farm')
        lat = float(data.get('latitude', 41.1579))
        lon = float(data.get('longitude', -8.6291))
        
        # Get weather data
        weather_data = weather_service.get_weather_data(location, lat, lon)
        if not weather_data:
            return jsonify({
                "success": False,
                "error": "Could not fetch weather data"
            }), 500
        
        # Get agricultural suggestions
        suggestion = agro_service.analyze_weather_for_agriculture(weather_data)
        
        if suggestion:
            return jsonify({
                "success": True,
                "weather": weather_data.to_dict(),
                "agro_suggestions": suggestion.to_dict()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not generate agricultural suggestions"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/agro/quick-analyze', methods=['POST'])
@token_required
def quick_agro_analysis(current_user):
    """Quick agricultural analysis with manual weather input"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        temperature = float(data.get('temperature', 20))
        humidity = float(data.get('humidity', 60))
        description = data.get('description', 'Clear sky')
        location = data.get('location', 'Farm')
        
        suggestion = agro_service.get_simple_suggestions(
            temperature, humidity, description, location
        )
        
        if suggestion:
            return jsonify({
                "success": True,
                "agro_suggestions": suggestion.to_dict()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not generate suggestions"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/agro/bulk-analyze', methods=['POST'])
@token_required
def bulk_agro_analysis(current_user):
    """Analyze multiple locations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        locations = data.get('locations', [])
        if not locations:
            return jsonify({"error": "No locations provided"}), 400
        
        weather_data_list = []
        for loc_data in locations:
            location = loc_data.get('name', 'Unknown')
            lat = float(loc_data.get('latitude', 0))
            lon = float(loc_data.get('longitude', 0))
            
            weather = weather_service.get_weather_data(location, lat, lon)
            if weather:
                weather_data_list.append(weather)
        
        suggestions = agro_service.get_suggestions_for_locations(weather_data_list)
        
        return jsonify({
            "success": True,
            "analyzed_locations": len(suggestions),
            "suggestions": [sug.to_dict() for sug in suggestions]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/agro/cache-info', methods=['GET'])
@token_required
def get_agro_cache_info(current_user):
    """Get agro service cache information"""
    cache_info = agro_service.get_cache_info()
    return jsonify({
        "success": True,
        "cache_info": cache_info
    })

@app.route('/api/agro/observer-stats', methods=['GET'])
@token_required
def get_observer_stats(current_user):
    """Get observer statistics"""
    stats = log_observer.get_event_stats()
    return jsonify({
        "success": True,
        "observer_stats": stats
    })

@app.route('/api/websocket/stats', methods=['GET'])
@token_required
def get_websocket_stats(current_user):
    """Get WebSocket connection statistics"""
    stats = websocket_service.get_stats()
    return jsonify({
        "success": True,
        "websocket_stats": stats
    })

@app.route('/api/weather/test-api', methods=['GET'])
@token_required
def test_weather_api(current_user):
    """Test OpenWeatherMap API connection"""
    api_working = weather_service.test_api_connection()
    cache_info = weather_service.get_cache_info()
    
    return jsonify({
        "success": True,
        "api_connected": api_working,
        "cache_info": cache_info
    })

@app.route('/api/system/trigger-alert', methods=['POST'])
@token_required
def trigger_weather_alert(current_user):
    """Manually trigger a weather alert for testing"""
    try:
        data = request.get_json()
        location = data.get('location', 'Test Location')
        alert_type = data.get('alert_type', 'test')
        message = data.get('message', 'Test weather alert')
        priority = data.get('priority', 'medium')
        
        websocket_service.send_weather_alert(location, alert_type, message, priority)
        
        return jsonify({
            "success": True,
            "message": "Weather alert sent via WebSocket"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "FarmVille API Gateway",
        "services": {
            "user_service": "active",
            "weather_service": "active", 
            "agro_service": "active"
        }
    })

if __name__ == '__main__':
    print("🌾 FarmVille API Gateway starting...")
    print("📡 Server: http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)