from flask import Blueprint, request, jsonify, current_app
from api.routes.auth_routes import token_required

terrain_bp = Blueprint('terrain', __name__)

@terrain_bp.route('', methods=['POST'])
@token_required
def create_terrain(current_user):
    """
    Create new terrain (original method maintained for compatibility)
    
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
        JSON response with terrain creation result
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        name = data.get('name')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        crop_type = data.get('crop_type')
        area_hectares = data.get('area_hectares')
        notes = data.get('notes')
        
        if not all([name, latitude is not None, longitude is not None]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: name, latitude, longitude"
            }), 400
        
        result = current_app.terrain_service.create_terrain(
            user_id=current_user['id'],
            name=name,
            latitude=float(latitude),
            longitude=float(longitude),
            crop_type=crop_type,
            area_hectares=float(area_hectares) if area_hectares else None,
            notes=notes
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

@terrain_bp.route('/with-location', methods=['POST'])
@token_required
def create_terrain_with_location(current_user):
    """
    Create new terrain using parish ID (new location-based method)
    
    Args:
        current_user: Authenticated user object
        
    Request Body:
        name (str): Terrain name
        parish_id (int): Parish ID
        crop_type (str, optional): Type of crop
        area_hectares (float, optional): Area in hectares
        notes (str, optional): Additional notes
        
    Returns:
        JSON response with terrain creation result
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        name = data.get('name')
        parish_id = data.get('parish_id')
        crop_type = data.get('crop_type')
        area_hectares = data.get('area_hectares')
        notes = data.get('notes')
        
        if not all([name, parish_id]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: name, parish_id"
            }), 400
        
        result = current_app.terrain_service.create_terrain_with_location(
            user_id=current_user['id'],
            name=name,
            parish_id=int(parish_id),
            crop_type=crop_type,
            area_hectares=float(area_hectares) if area_hectares else None,
            notes=notes
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
def get_terrains(current_user):
    """
    Get all terrains for authenticated user
    
    Args:
        current_user: Authenticated user object
        
    Returns:
        JSON response with list of terrains
    """
    try:
        result = current_app.terrain_service.get_user_terrains(current_user['id'])
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@terrain_bp.route('/by-location', methods=['GET'])
@token_required
def get_terrains_by_location(current_user):
    """
    Get terrains filtered by location
    
    Args:
        current_user: Authenticated user object
        
    Query Parameters:
        district_id (int, optional): District ID
        municipality_id (int, optional): Municipality ID
        parish_id (int, optional): Parish ID
        
    Returns:
        JSON response with filtered terrains
    """
    try:
        district_id = request.args.get('district_id', type=int)
        municipality_id = request.args.get('municipality_id', type=int)
        parish_id = request.args.get('parish_id', type=int)
        
        result = current_app.terrain_service.get_terrains_by_location(
            user_id=current_user['id'],
            district_id=district_id,
            municipality_id=municipality_id,
            parish_id=parish_id
        )
        
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
    Get specific terrain
    
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
    Update terrain (enhanced with location support)
    
    Args:
        current_user: Authenticated user object
        terrain_id (int): Terrain ID
        
    Request Body:
        name (str, optional): Terrain name
        latitude (float, optional): Latitude coordinate
        longitude (float, optional): Longitude coordinate
        parish_id (int, optional): Parish ID (will update location and coordinates)
        crop_type (str, optional): Type of crop
        area_hectares (float, optional): Area in hectares
        notes (str, optional): Additional notes
        
    Returns:
        JSON response with update result
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        # Extract update data
        updates = {}
        for field in ['name', 'latitude', 'longitude', 'parish_id', 'crop_type', 'area_hectares', 'notes']:
            if field in data:
                updates[field] = data[field]
        
        result = current_app.terrain_service.update_terrain(
            terrain_id, current_user['id'], **updates
        )
        
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
    Get terrain statistics for the authenticated user (enhanced with location stats)
    
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
        result = current_app.terrain_service.get_terrain_weather(
            terrain_id, current_user['id'], current_app.weather_service
        )
        
        status = 200 if result['success'] else 404
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500