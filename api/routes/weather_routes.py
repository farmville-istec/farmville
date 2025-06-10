from flask import Blueprint, request, jsonify, current_app
from api.routes.auth_routes import token_required

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/<location>', methods=['GET'])
@token_required
def get_weather(current_user, location):
    """
    Get weather data for a specific location
    
    Args:
        current_user: Authenticated user object
        location (str): Location name
        
    Query Parameters:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        
    Returns:
        JSON response with weather data
    """
    try:
        lat = float(request.args.get('lat', 41.1579))
        lon = float(request.args.get('lon', -8.6291))
        
        weather_data = current_app.weather_service.get_weather_data(location, lat, lon)
        
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