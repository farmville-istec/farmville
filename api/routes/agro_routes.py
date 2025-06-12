from flask import Blueprint, request, jsonify, current_app
from api.routes.auth_routes import token_required

agro_bp = Blueprint('agro', __name__)

@agro_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_weather_for_agriculture(current_user):
    """
    Analyze weather data and provide agricultural suggestions
    
    Args:
        current_user: Authenticated user object
        
    Request Body:
        location (str): Farm location name
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        
    Returns:
        JSON response with weather data and agricultural suggestions
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        location = data.get('location', 'Farm')
        lat = float(data.get('latitude', 41.1579))
        lon = float(data.get('longitude', -8.6291))
        
        weather_data = current_app.weather_service.get_weather_data(location, lat, lon)
        if not weather_data:
            return jsonify({
                "success": False,
                "error": "Could not fetch weather data"
            }), 500
        
        suggestion = current_app.agro_service.analyze_weather_for_agriculture(weather_data)
        
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

@agro_bp.route('/quick-analyze', methods=['POST'])
@token_required
def quick_agro_analysis(current_user):
    """
    Quick agricultural analysis with manual weather input
    
    Args:
        current_user: Authenticated user object
        
    Request Body:
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage
        description (str): Weather description
        location (str): Location name
        
    Returns:
        JSON response with agricultural suggestions
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        temperature = float(data.get('temperature', 20))
        humidity = float(data.get('humidity', 60))
        description = data.get('description', 'Clear sky')
        location = data.get('location', 'Farm')
        
        suggestion = current_app.agro_service.get_simple_suggestions(
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

@agro_bp.route('/bulk-analyze', methods=['POST'])
@token_required
def bulk_agro_analysis(current_user):
    """
    Analyze multiple locations for agricultural insights
    
    Args:
        current_user: Authenticated user object
        
    Request Body:
        locations (list): List of location objects with name, latitude, longitude
        
    Returns:
        JSON response with analysis results for all locations
    """
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
            
            weather = current_app.weather_service.get_weather_data(location, lat, lon)
            if weather:
                weather_data_list.append(weather)
        
        suggestions = current_app.agro_service.get_suggestions_for_locations(weather_data_list)
        
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

@agro_bp.route('/cache-info', methods=['GET'])
@token_required
def get_agro_cache_info(current_user):
    """
    Get agricultural service cache information
    
    Args:
        current_user: Authenticated user object
        
    Returns:
        JSON response with cache statistics
    """
    cache_info = current_app.agro_service.get_cache_info()
    return jsonify({
        "success": True,
        "cache_info": cache_info
    })

@agro_bp.route('/observer-stats', methods=['GET'])
@token_required
def get_observer_stats(current_user):
    """
    Get observer pattern statistics for monitoring
    
    Args:
        current_user: Authenticated user object
        
    Returns:
        JSON response with observer statistics
    """
    # This would need to be connected to the actual observer instance
    # For now, return basic stats
    return jsonify({
        "success": True,
        "observer_stats": {
            "total_events": 0,
            "event_breakdown": {}
        }
    })