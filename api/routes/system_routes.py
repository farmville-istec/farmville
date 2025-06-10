from flask import Blueprint, jsonify, current_app
from api.routes.auth_routes import token_required

system_bp = Blueprint('system', __name__)

@system_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for deployment monitoring
    
    Returns:
        JSON response with system health status
    """
    return jsonify({
        "status": "healthy",
        "service": "FarmVille API Gateway",
        "services": {
            "user_service": "active",
            "weather_service": "active", 
            "agro_service": "active",
            "terrain_service": "active"
        }
    })