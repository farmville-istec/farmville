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
    print("📡 Server: http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)