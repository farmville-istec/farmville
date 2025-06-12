from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
from flask_socketio import SocketIO # type: ignore
from dotenv import load_dotenv
from functools import wraps

from services.user_service import UserService
from services.location_service import LocationService
from services.terrain_service import TerrainService
from services.weather_service import WeatherService
from services.agro_service import AgroService
from services.websocket_service import WebSocketService, setup_websocket_handlers
from utils.observers.agro_observer import AgroAlertObserver, AgroLogObserver

load_dotenv()

def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    CORS(app)
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize services in correct order (location service first)
    user_service = UserService()
    location_service = LocationService()
    terrain_service = TerrainService(location_service)  # Inject location service
    weather_service = WeatherService()
    agro_service = AgroService()
    websocket_service = WebSocketService(socketio)
    
    # Setup observers
    alert_observer = AgroAlertObserver()
    log_observer = AgroLogObserver()
    
    agro_service.attach(alert_observer)
    agro_service.attach(log_observer)
    agro_service.attach(websocket_service)
    weather_service.attach(websocket_service)
    
    setup_websocket_handlers(socketio, websocket_service)
    
    # Attach services to app
    app.user_service = user_service
    app.location_service = location_service
    app.terrain_service = terrain_service
    app.weather_service = weather_service
    app.agro_service = agro_service
    app.websocket_service = websocket_service
    
    # ==================== AUTH DECORATOR ====================
    def token_required(f):
        """Decorator for routes that require authentication"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
            
            if not token:
                return jsonify({'error': 'Missing token'}), 401
            
            user = app.user_service.get_user_from_token(token)
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
            
            return f(user, *args, **kwargs)
        return decorated
    
    # ==================== AUTH ROUTES ====================
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register a new user"""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        result = app.user_service.register_user(
            data.get('username', ''),
            data.get('password', ''),
            data.get('email', '')
        )
        
        status = 201 if result['success'] else 400
        return jsonify(result), status
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Authenticate user and return JWT token"""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        result = app.user_service.login_user(
            data.get('username', ''),
            data.get('password', '')
        )
        
        status = 200 if result['success'] else 401
        return jsonify(result), status
    
    @app.route('/api/auth/profile', methods=['GET'])
    @token_required
    def profile(current_user):
        """Get current user profile information"""
        return jsonify({"user": current_user})
    
    # ==================== LOCATION ROUTES ====================
    @app.route('/api/location/hierarchy', methods=['GET'])
    @token_required
    def get_location_hierarchy(current_user):
        """Get complete Portuguese location hierarchy"""
        try:
            hierarchy = app.location_service.get_location_hierarchy()
            
            if hierarchy:
                return jsonify({
                    "success": True,
                    "hierarchy": hierarchy.to_dict()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Could not fetch location hierarchy"
                }), 500
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/location/coordinates', methods=['POST'])
    @token_required
    def get_coordinates(current_user):
        """Get coordinates for a specific Portuguese location"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing data"}), 400
            
            district = data.get('district', '').strip()
            municipality = data.get('municipality', '').strip()
            parish = data.get('parish', '').strip()
            
            if not all([district, municipality, parish]):
                return jsonify({
                    "success": False,
                    "error": "District, municipality and parish are required"
                }), 400
            
            location = app.location_service.get_coordinates_for_location(
                district, municipality, parish
            )
            
            if location:
                return jsonify({
                    "success": True,
                    "location": location.to_dict()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Location not found"
                }), 404
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/location/search', methods=['GET'])
    @token_required
    def search_locations(current_user):
        """Search for locations by name"""
        try:
            query = request.args.get('q', '').strip()
            
            if not query:
                return jsonify({
                    "success": False,
                    "error": "Search query is required"
                }), 400
            
            if len(query) < 2:
                return jsonify({
                    "success": False,
                    "error": "Search query must be at least 2 characters"
                }), 400
            
            results = app.location_service.search_locations(query)
            
            return jsonify({
                "success": True,
                "results": results,
                "count": len(results)
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    # ==================== TERRAIN ROUTES ====================
    @app.route('/api/terrains', methods=['POST'])
    @token_required
    def create_terrain(current_user):
        """Create a new terrain"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing data"}), 400
            
            # Extract coordinates (optional if location provided)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            # Extract administrative location (optional if coordinates provided)
            district = data.get('district')
            municipality = data.get('municipality')
            parish = data.get('parish')
            
            # Convert coordinate strings to floats if provided
            if latitude is not None:
                latitude = float(latitude)
            if longitude is not None:
                longitude = float(longitude)
            
            result = app.terrain_service.create_terrain(
                user_id=current_user['id'],
                name=data.get('name', ''),
                latitude=latitude,
                longitude=longitude,
                district=district,
                municipality=municipality,
                parish=parish,
                crop_type=data.get('crop_type'),
                area_hectares=float(data['area_hectares']) if data.get('area_hectares') else None,
                notes=data.get('notes')
            )
            
            status = 201 if result['success'] else 400
            return jsonify(result), status
            
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"Invalid input data: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/terrains/with-location', methods=['POST'])
    @token_required
    def create_terrain_with_location(current_user):
        """Create a new terrain using Portuguese administrative location"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing data"}), 400
            
            result = app.terrain_service.create_terrain_with_location(
                user_id=current_user['id'],
                name=data.get('name', ''),
                district=data.get('district', ''),
                municipality=data.get('municipality', ''),
                parish=data.get('parish', ''),
                crop_type=data.get('crop_type'),
                area_hectares=float(data['area_hectares']) if data.get('area_hectares') else None,
                notes=data.get('notes')
            )
            
            status = 201 if result['success'] else 400
            return jsonify(result), status
            
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"Invalid input data: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/terrains', methods=['GET'])
    @token_required
    def get_user_terrains(current_user):
        """Get all terrains for the authenticated user"""
        try:
            result = app.terrain_service.get_user_terrains(current_user['id'])
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/terrains/by-location', methods=['GET'])
    @token_required
    def get_terrains_by_location(current_user):
        """Get terrains filtered by Portuguese administrative location"""
        try:
            district = request.args.get('district')
            municipality = request.args.get('municipality')
            parish = request.args.get('parish')
            
            result = app.terrain_service.get_terrains_by_location(
                district=district,
                municipality=municipality,
                parish=parish
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/terrains/<int:terrain_id>', methods=['GET'])
    @token_required
    def get_terrain(current_user, terrain_id):
        """Get specific terrain by ID"""
        try:
            result = app.terrain_service.get_terrain(terrain_id, current_user['id'])
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
        """Update terrain information"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing data"}), 400
            
            updates = {}
            
            if 'name' in data:
                updates['name'] = data['name']
            
            if 'latitude' in data:
                updates['latitude'] = float(data['latitude'])
            
            if 'longitude' in data:
                updates['longitude'] = float(data['longitude'])
            
            # Administrative location updates
            if 'district' in data:
                updates['district'] = data['district']
            
            if 'municipality' in data:
                updates['municipality'] = data['municipality']
            
            if 'parish' in data:
                updates['parish'] = data['parish']
            
            if 'crop_type' in data:
                updates['crop_type'] = data['crop_type']
            
            if 'area_hectares' in data:
                updates['area_hectares'] = float(data['area_hectares']) if data['area_hectares'] else None
            
            if 'notes' in data:
                updates['notes'] = data['notes']
            
            result = app.terrain_service.update_terrain(terrain_id, current_user['id'], **updates)
            status = 200 if result['success'] else 400
            return jsonify(result), status
            
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"Invalid input data: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/terrains/<int:terrain_id>', methods=['DELETE'])
    @token_required
    def delete_terrain(current_user, terrain_id):
        """Delete terrain"""
        try:
            result = app.terrain_service.delete_terrain(terrain_id, current_user['id'])
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
        """Get terrain statistics with location breakdown"""
        try:
            result = app.terrain_service.get_terrain_stats(current_user['id'])
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/terrains/<int:terrain_id>/weather', methods=['GET'])
    @token_required
    def get_terrain_weather(current_user, terrain_id):
        """Get weather data for a specific terrain"""
        try:
            terrain_result = app.terrain_service.get_terrain(terrain_id, current_user['id'])
            
            if not terrain_result['success']:
                return jsonify(terrain_result), 404
            
            terrain = terrain_result['terrain']
            
            # Use terrain's full location name if available, otherwise just the terrain name
            location_name = terrain.get('full_location') or terrain['name']
            
            weather_data = app.weather_service.get_weather_data(
                location_name, 
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
        """Get agricultural analysis for a specific terrain"""
        try:
            terrain_result = app.terrain_service.get_terrain(terrain_id, current_user['id'])
            
            if not terrain_result['success']:
                return jsonify(terrain_result), 404
            
            terrain = terrain_result['terrain']
            
            # Use terrain's full location name if available, otherwise just the terrain name
            location_name = terrain.get('full_location') or terrain['name']
            
            weather_data = app.weather_service.get_weather_data(
                location_name, 
                terrain['latitude'], 
                terrain['longitude']
            )
            
            if not weather_data:
                return jsonify({
                    "success": False,
                    "error": "Could not fetch weather data"
                }), 500
            
            suggestion = app.agro_service.analyze_weather_for_agriculture(weather_data)
            
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
    
    # ==================== WEATHER ROUTES ====================
    @app.route('/api/weather/<location>', methods=['GET'])
    @token_required
    def get_weather(current_user, location):
        """Get weather data for a specific location"""
        try:
            lat = float(request.args.get('lat', 41.1579))
            lon = float(request.args.get('lon', -8.6291))
            
            weather_data = app.weather_service.get_weather_data(location, lat, lon)
            
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
                
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"Invalid coordinates: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    # ==================== AGRO ROUTES ====================
    @app.route('/api/agro/analyze', methods=['POST'])
    @token_required
    def analyze_weather_for_agriculture(current_user):
        """Analyze weather data and provide agricultural suggestions"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Missing data"}), 400
            
            location = data.get('location', 'Farm')
            lat = float(data.get('latitude', 41.1579))
            lon = float(data.get('longitude', -8.6291))
            
            weather_data = app.weather_service.get_weather_data(location, lat, lon)
            if not weather_data:
                return jsonify({
                    "success": False,
                    "error": "Could not fetch weather data"
                }), 500
            
            suggestion = app.agro_service.analyze_weather_for_agriculture(weather_data)
            
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
                
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"Invalid input data: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/agro/bulk-analyze', methods=['POST'])
    @token_required
    def bulk_agro_analysis(current_user):
        """Analyze multiple locations for agricultural insights"""
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
                
                weather = app.weather_service.get_weather_data(location, lat, lon)
                if weather:
                    weather_data_list.append(weather)
            
            suggestions = app.agro_service.get_suggestions_for_locations(weather_data_list)
            
            return jsonify({
                "success": True,
                "analyzed_locations": len(suggestions),
                "suggestions": [sug.to_dict() for sug in suggestions]
            })
            
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": f"Invalid input data: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    # ==================== SYSTEM ROUTES ====================
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "FarmVille API Gateway",
            "services": {
                "user_service": "active",
                "location_service": "active",
                "weather_service": "active", 
                "agro_service": "active",
                "terrain_service": "active"
            }
        })
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    print("🚜 FarmVille API Gateway starting...")
    print("📍 Location Service (GeoAPI.pt) integrated")
    print("🌱 Enhanced Terrain Service with administrative divisions")
    print("🌐 Server: http://0.0.0.0:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)