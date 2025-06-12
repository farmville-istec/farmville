from flask import Flask
from flask_cors import CORS # type: ignore
from flask_socketio import SocketIO # type: ignore
from dotenv import load_dotenv

from services.user_service import UserService
from services.terrain_service import TerrainService
from services.weather_service import WeatherService
from services.agro_service import AgroService
from services.websocket_service import WebSocketService, setup_websocket_handlers
from utils.observers.agro_observer import AgroAlertObserver, AgroLogObserver

from api.routes.auth_routes import auth_bp
from api.routes.weather_routes import weather_bp
from api.routes.agro_routes import agro_bp
from api.routes.terrain_routes import terrain_bp
from api.routes.system_routes import system_bp

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
    
    user_service = UserService()
    terrain_service = TerrainService()
    weather_service = WeatherService()
    agro_service = AgroService()
    websocket_service = WebSocketService(socketio)
    
    alert_observer = AgroAlertObserver()
    log_observer = AgroLogObserver()
    
    agro_service.attach(alert_observer)
    agro_service.attach(log_observer)
    agro_service.attach(websocket_service)
    weather_service.attach(websocket_service)
    
    setup_websocket_handlers(socketio, websocket_service)
    
    app.user_service = user_service
    app.terrain_service = terrain_service
    app.weather_service = weather_service
    app.agro_service = agro_service
    app.websocket_service = websocket_service
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(agro_bp, url_prefix='/api/agro')
    app.register_blueprint(terrain_bp, url_prefix='/api/terrains')
    app.register_blueprint(system_bp)
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    print("FarmVille API Gateway starting...")
    print("Server: http://0.0.0.0:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)