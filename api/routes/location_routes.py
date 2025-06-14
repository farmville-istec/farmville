from flask import Blueprint, request, jsonify, current_app
from api.routes.auth_routes import token_required

location_bp = Blueprint('location', __name__)

@location_bp.route('/districts', methods=['GET'])
@token_required
def get_districts(current_user):
    """
    Get all Portuguese districts
    
    Args:
        current_user: Authenticated user object
        
    Returns:
        JSON response with list of districts
    """
    try:
        districts = current_app.location_service.get_districts()
        
        if districts:
            return jsonify({
                "success": True,
                "districts": districts
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not fetch districts"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@location_bp.route('/municipalities', methods=['GET'])
@token_required
def get_municipalities(current_user):
    """
    Get municipalities for a specific district
    
    Args:
        current_user: Authenticated user object
        
    Query Parameters:
        district_id (int): District ID
        
    Returns:
        JSON response with list of municipalities
    """
    try:
        district_id = request.args.get('district_id', type=int)
        if not district_id:
            return jsonify({
                "success": False,
                "error": "Missing district_id parameter"
            }), 400
        
        municipalities = current_app.location_service.get_municipalities(district_id)
        
        if municipalities:
            return jsonify({
                "success": True,
                "municipalities": municipalities
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not fetch municipalities"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@location_bp.route('/parishes', methods=['GET'])
@token_required
def get_parishes(current_user):
    """
    Get parishes for a specific municipality
    
    Args:
        current_user: Authenticated user object
        
    Query Parameters:
        municipality_id (int): Municipality ID
        
    Returns:
        JSON response with list of parishes
    """
    try:
        municipality_id = request.args.get('municipality_id', type=int)
        if not municipality_id:
            return jsonify({
                "success": False,
                "error": "Missing municipality_id parameter"
            }), 400
        
        parishes = current_app.location_service.get_parishes(municipality_id)
        
        if parishes:
            return jsonify({
                "success": True,
                "parishes": parishes
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not fetch parishes"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@location_bp.route('/coordinates', methods=['GET'])
@token_required
def get_parish_coordinates(current_user):
    """
    Get coordinates for a specific parish
    
    Args:
        current_user: Authenticated user object
        
    Query Parameters:
        parish_id (int): Parish ID
        
    Returns:
        JSON response with parish coordinates
    """
    try:
        parish_id = request.args.get('parish_id', type=int)
        if not parish_id:
            return jsonify({
                "success": False,
                "error": "Missing parish_id parameter"
            }), 400
        
        coordinates = current_app.location_service.get_parish_coordinates(parish_id)
        
        if coordinates:
            return jsonify({
                "success": True,
                "coordinates": coordinates
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not fetch coordinates"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@location_bp.route('/hierarchy', methods=['GET'])
@token_required
def get_location_hierarchy(current_user):
    """
    Get complete location hierarchy and coordinates for a parish
    
    Args:
        current_user: Authenticated user object
        
    Query Parameters:
        parish_id (int): Parish ID
        
    Returns:
        JSON response with complete location data
    """
    try:
        parish_id = request.args.get('parish_id', type=int)
        if not parish_id:
            return jsonify({
                "success": False,
                "error": "Missing parish_id parameter"
            }), 400
        
        hierarchy = current_app.location_service.get_location_hierarchy(parish_id)
        
        if hierarchy:
            return jsonify({
                "success": True,
                "location": hierarchy
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

@location_bp.route('/weather', methods=['GET'])
@token_required
def get_location_weather(current_user):
    """
    Get weather data for a selected location by parish ID
    
    Args:
        current_user: Authenticated user object
        
    Query Parameters:
        parish_id (int): Parish ID
        
    Returns:
        JSON response with location info and weather data
    """
    try:
        parish_id = request.args.get('parish_id', type=int)
        if not parish_id:
            return jsonify({
                "success": False,
                "error": "Missing parish_id parameter"
            }), 400
        
        # Get location hierarchy
        hierarchy = current_app.location_service.get_location_hierarchy(parish_id)
        if not hierarchy:
            return jsonify({
                "success": False,
                "error": "Could not fetch location data"
            }), 500
        
        coordinates = hierarchy.get('coordinates', {})
        if not coordinates.get('latitude') or not coordinates.get('longitude'):
            return jsonify({
                "success": False,
                "error": "Location coordinates not available"
            }), 500
        
        # Get weather data for the location
        location_name = f"{hierarchy['parish']['nome']}, {hierarchy['municipality']['nome']}"
        weather_data = current_app.weather_service.get_weather_data(
            location_name,
            coordinates['latitude'],
            coordinates['longitude']
        )
        
        if weather_data:
            return jsonify({
                "success": True,
                "location": hierarchy,
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