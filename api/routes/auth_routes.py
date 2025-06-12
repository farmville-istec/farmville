from flask import Blueprint, request, jsonify, current_app
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """
    Decorator for routes that require authentication
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function that validates JWT tokens
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        user = current_app.user_service.get_user_from_token(token)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Returns:
        JSON response with registration result
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    
    result = current_app.user_service.register_user(
        data.get('username', ''),
        data.get('password', ''),
        data.get('email', '')
    )
    
    status = 201 if result['success'] else 400
    return jsonify(result), status

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token
    
    Returns:
        JSON response with login result and token
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    
    result = current_app.user_service.login_user(
        data.get('username', ''),
        data.get('password', '')
    )
    
    status = 200 if result['success'] else 401
    return jsonify(result), status

@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    """
    Get current user profile information
    
    Args:
        current_user: User object from token validation
        
    Returns:
        JSON response with user profile data
    """
    return jsonify({"user": current_user})