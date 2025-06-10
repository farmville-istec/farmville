from flask import Blueprint, request, jsonify, current_app
from api.routes.auth_routes import token_required

terrain_bp = Blueprint('terrain', __name__)

@terrain_bp.route('', methods=['POST'])
@token_required
def create_terrain(current_user):
    """
    Create a new terrain for the authenticated user
    
    Args:
        current_user: Authenticated user object
        
    Request Body:
        name (str): Terrain name
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        crop_type (str, optional): Type of crop
        area_hectares (float, optional): Area in hectares
        notes (str, optional): Additional notes
        
    Returns:
        JSON response with creation result
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        result = current_app.terrain_service.create_terrain(
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

@terrain_bp.route('', methods=['GET'])
@token_required
def get_user_terrains(current_user):
    """
    Get all terrains for the authenticated user
    
    Args:
        current_user: Authenticated user object
        
    Returns:
        JSON response with user's terrains
    """
    try:
        result = current_app.terrain_service.get_user_terrains(current_user['id'])
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@terrain_bp.route('/<int:terrain_id>', methods=['GET'])
@token_required
def get_terrain(current_user, terrain_id):
    """
    Get specific terrain by ID (if owned by user)
    
    Args:
        current_user: Authenticated user object
        terrain_id (int): Terrain ID
        
    Returns:
        JSON response with terrain data
    """
    try:
        result = current_app.terrain_service.get_terrain(terrain_id, current_user['id'])
        status = 200 if result['success'] else 404
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@terrain_bp.route('/<int:terrain_id>', methods=['PUT'])
@token_required
def update_terrain(current_user, terrain_id):
    """
    Update terrain information
    
    Args:
        current_user: Authenticated user object
        terrain_id (int): Terrain ID
        
    Request Body:
        name (str, optional): New terrain name
        latitude (float, optional): New latitude
        longitude (float, optional): New longitude
        crop_type (str, optional): New crop type
        area_hectares (float, optional): New area
        notes (str, optional): New notes
        
    Returns:
        JSON response with update result
    """
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
        
        if 'crop_type' in data:
            updates['crop_type'] = data['crop_type']
        
        if 'area_hectares' in data:
            updates['area_hectares'] = float(data['area_hectares']) if data['area_hectares'] else None
        
        if 'notes' in data:
            updates['notes'] = data['notes']
        
        result = current_app.terrain_service.update_terrain(terrain_id, current_user['id'], **updates)
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

@terrain_bp.route('/<int:terrain_id>', methods=['DELETE'])
@token_required
def delete_terrain(current_user, terrain_id):
    """
    Delete terrain
    
    Args:
        current_user: Authenticated user object
        terrain_id (int): Terrain ID
        
    Returns:
        JSON response with deletion result
    """
    try:
        result = current_app.terrain_service.delete_terrain(terrain_id, current_user['id'])
        status = 200 if result['success'] else 400
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@terrain_bp.route('/stats', methods=['GET'])
@token_required
def get_terrain_stats(current_user):
    """
    Get terrain statistics for the authenticated user
    
    Args:
        current_user: Authenticated user object
        
    Returns:
        JSON response with terrain statistics
    """
    try:
        result = current_app.terrain_service.get_terrain_stats(current_user['id'])
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@terrain_bp.route('/<int:terrain_id>/weather', methods=['GET'])
@token_required
def get_terrain_weather(current_user, terrain_id):
    """
    Get weather data for a specific terrain
    
    Args:
        current_user: Authenticated user object
        terrain_id (int): Terrain ID
        
    Returns:
        JSON response with terrain and weather data
    """
    try:
        terrain_result = current_app.terrain_service.get_terrain(terrain_id, current_user['id'])
        
        if not terrain_result['success']:
            return jsonify(terrain_result), 404
        
        terrain = terrain_result['terrain']
        
        weather_data = current_app.weather_service.get_weather_data(
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

@terrain_bp.route('/<int:terrain_id>/agro-analysis', methods=['POST'])
@token_required
def get_terrain_agro_analysis(current_user, terrain_id):
    """
    Get agricultural analysis for a specific terrain
    
    Args:
        current_user: Authenticated user object
        terrain_id (int): Terrain ID
        
    Returns:
        JSON response with terrain, weather data, and agricultural suggestions
    """
    try:
        terrain_result = current_app.terrain_service.get_terrain(terrain_id, current_user['id'])
        
        if not terrain_result['success']:
            return jsonify(terrain_result), 404
        
        terrain = terrain_result['terrain']
        
        weather_data = current_app.weather_service.get_weather_data(
            terrain['name'], 
            terrain['latitude'], 
            terrain['longitude']
        )
        
        if not weather_data:
            return jsonify({
                "success": False,
                "error": "Could not fetch weather data"
            }), 500
        
        suggestion = current_app.agro_service.analyze_weather_for_agriculture(weather_data)
        
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