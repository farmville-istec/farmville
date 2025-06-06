"""
API Gateway for FarmVille
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from services.user_service import UserService
from services.weather_service import WeatherService
from dotenv import load_dotenv
from services.location_service import LocationService

load_dotenv()

app = Flask(__name__)
CORS(app)

user_service = UserService()
weather_service = WeatherService()
location_service = LocationService()

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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "FarmVille API Gateway"
    })

if __name__ == '__main__':
    print("🌾 FarmVille API Gateway starting...")
    print("📡 Server: http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5001, debug=True)
    
@app.route('/api/locations/address', methods=['POST'])
@token_required
def create_location_from_address(current_user):
    """
    Create location from address using geocoding
    
    Expected JSON:
    {
        "address": "123 Main St, City, Country",
        "name": "My Farm Location",
        "country": "pt"  // optional
    }
    """
    data = request.get_json()
    if not data or not data.get('address'):
        return jsonify({"error": "Address is required"}), 400
    
    result = location_service.create_location_from_address(
        address=data['address'],
        name=data.get('name'),
        user_id=current_user['id'],
        country=data.get('country')
    )
    
    status = 201 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/locations/coordinates', methods=['POST'])
@token_required
def create_location_from_coordinates(current_user):
    """
    Create location from coordinates
    
    Expected JSON:
    {
        "latitude": 41.1579,
        "longitude": -8.6291,
        "name": "My Farm Point"
    }
    """
    data = request.get_json()
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinate values"}), 400
    
    result = location_service.create_location_from_coordinates(
        latitude=latitude,
        longitude=longitude,
        name=data.get('name'),
        user_id=current_user['id']
    )
    
    status = 201 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/locations/area', methods=['POST'])
@token_required
def create_location_from_area(current_user):
    """
    Create location from drawn area (GeoJSON polygon)
    
    Expected JSON:
    {
        "name": "My Farm Area",
        "geojson_polygon": {
            "type": "Polygon",
            "coordinates": [[[lng, lat], [lng, lat], ...]]
        }
    }
    """
    data = request.get_json()
    if not data or not data.get('name') or not data.get('geojson_polygon'):
        return jsonify({"error": "Name and geojson_polygon are required"}), 400
    
    result = location_service.create_location_from_area(
        geojson_polygon=data['geojson_polygon'],
        name=data['name'],
        user_id=current_user['id']
    )
    
    status = 201 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/locations/search', methods=['GET'])
@token_required
def search_locations(current_user):
    """
    Search locations by query
    
    Query parameters:
    - q: search query
    - proximity_lat: optional latitude for proximity bias
    - proximity_lng: optional longitude for proximity bias
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    proximity = None
    proximity_lat = request.args.get('proximity_lat')
    proximity_lng = request.args.get('proximity_lng')
    
    if proximity_lat and proximity_lng:
        try:
            proximity = (float(proximity_lat), float(proximity_lng))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid proximity coordinates"}), 400
    
    result = location_service.search_locations(
        query=query,
        user_id=current_user['id'],
        proximity=proximity
    )
    
    status = 200 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/locations', methods=['GET'])
@token_required
def get_user_locations(current_user):
    """
    Get all locations for current user
    
    Query parameters:
    - include_weather: true/false to include weather data
    """
    include_weather = request.args.get('include_weather', '').lower() == 'true'
    
    result = location_service.get_user_locations(
        user_id=current_user['id'],
        include_weather=include_weather
    )
    
    status = 200 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/locations/<int:location_id>', methods=['GET'])
@token_required
def get_location_with_weather(current_user, location_id):
    """Get specific location with weather data"""
    result = location_service.get_location_with_weather(
        location_id=location_id,
        user_id=current_user['id']
    )
    
    status = 200 if result['success'] else 404
    return jsonify(result), status

@app.route('/api/locations/<int:location_id>', methods=['PUT'])
@token_required
def update_location(current_user, location_id):
    """
    Update existing location
    
    Expected JSON (any combination):
    {
        "name": "Updated Name",
        "latitude": 41.1579,
        "longitude": -8.6291,
        "address": "Updated Address",
        "terrain_area": {...}
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Update data is required"}), 400
    
    result = location_service.update_location(
        location_id=location_id,
        updates=data,
        user_id=current_user['id']
    )
    
    status = 200 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
@token_required
def delete_location(current_user, location_id):
    """Delete location (soft delete)"""
    result = location_service.delete_location(
        location_id=location_id,
        user_id=current_user['id']
    )
    
    status = 200 if result['success'] else 404
    return jsonify(result), status

@app.route('/api/locations/nearby', methods=['GET'])
@token_required
def get_nearby_locations(current_user):
    """
    Get locations near a point
    
    Query parameters:
    - latitude: center latitude
    - longitude: center longitude
    - radius: radius in kilometers (default: 10)
    """
    try:
        latitude = float(request.args.get('latitude', 0))
        longitude = float(request.args.get('longitude', 0))
        radius = float(request.args.get('radius', 10))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinate or radius values"}), 400
    
    result = location_service.get_nearby_locations(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius,
        user_id=current_user['id']
    )
    
    status = 200 if result['success'] else 400
    return jsonify(result), status

@app.route('/api/locations/geocode', methods=['POST'])
@token_required
def geocode_address(current_user):
    """
    Geocode an address without saving it
    
    Expected JSON:
    {
        "address": "123 Main St, City, Country",
        "country": "pt"  // optional
    }
    """
    data = request.get_json()
    if not data or not data.get('address'):
        return jsonify({"error": "Address is required"}), 400
    
    try:
        # Direct use of mapbox client for one-time geocoding
        result = location_service.mapbox_client.geocode_address(
            data['address'],
            data.get('country')
        )
        
        if result:
            return jsonify({
                "success": True,
                "result": result
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Address not found"
            }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Geocoding error: {str(e)}"
        }), 500

@app.route('/api/locations/reverse-geocode', methods=['POST'])
@token_required
def reverse_geocode_coordinates(current_user):
    """
    Reverse geocode coordinates without saving
    
    Expected JSON:
    {
        "latitude": 41.1579,
        "longitude": -8.6291
    }
    """
    data = request.get_json()
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinate values"}), 400
    
    try:
        result = location_service.mapbox_client.reverse_geocode(latitude, longitude)
        
        if result:
            return jsonify({
                "success": True,
                "result": result
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Location not found"
            }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Reverse geocoding error: {str(e)}"
        }), 500

# Configuration endpoint for frontend
@app.route('/api/locations/config', methods=['GET'])
@token_required
def get_location_config(current_user):
    """
    Get configuration for frontend map integration
    """
    return jsonify({
        "mapbox": {
            "style_url": location_service.mapbox_client.get_map_style_url("satellite-v9"),
            "access_token": location_service.mapbox_client.access_token,
            "default_center": [41.1579, -8.6291],  # Porto, Portugal
            "default_zoom": 10
        },
        "limits": {
            "max_locations_per_user": 100,
            "max_area_size_sqkm": 1000,
            "search_radius_max_km": 100
        }
    }), 200
    