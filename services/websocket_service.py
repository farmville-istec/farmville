import logging
from typing import Set, Dict, Any
from datetime import datetime
import threading
import time

from flask_socketio import SocketIO, emit
from flask import request
from utils.patterns.observer import Observer

class WebSocketService(Observer):
    """
    Serviço WebSocket para comunicação em tempo real
    """
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients: Set[str] = set()
        self.client_subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of terrain_ids
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self._background_thread = None
        self._stop_background = False
        
        print("🔌 WebSocketService initialized")
    
    def start_background_updates(self):
        """Inicia thread de atualizações periódicas"""
        if self._background_thread is None or not self._background_thread.is_alive():
            self._stop_background = False
            self._background_thread = threading.Thread(
                target=self._periodic_update_worker,
                daemon=True
            )
            self._background_thread.start()
            print("🚀 Background update thread started")
    
    def stop_background_updates(self):
        """Para thread de atualizações periódicas"""
        self._stop_background = True
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=5)
            print("🛑 Background update thread stopped")
    
    def _periodic_update_worker(self):
        """
        Worker que roda em background thread para atualizações periódicas
        Atualiza dados meteorológicos a cada 10 minutos
        """
        print("⏰ Periodic update worker started")
        
        while not self._stop_background:
            try:
                # Sleep for 10 minutes (600 seconds)
                for _ in range(600):  # Check stop flag every second
                    if self._stop_background:
                        break
                    time.sleep(1)
                
                if not self._stop_background and self.connected_clients:
                    print("🔄 Triggering periodic weather update...")
                    self._broadcast_periodic_update()
                    
            except Exception as e:
                self.logger.error(f"Error in periodic update worker: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _broadcast_periodic_update(self):
        """Envia atualização periódica para todos os clientes conectados"""
        if not self.connected_clients:
            return
        
        update_data = {
            'type': 'periodic_update',
            'timestamp': datetime.now().isoformat(),
            'message': 'Checking for weather updates...'
        }
        
        self.socketio.emit('weather_update', update_data, broadcast=True)
        print(f"📡 Periodic update sent to {len(self.connected_clients)} clients")
    
    def update(self, subject, event_type: str, data: Any):
        """
        Implementação do Observer pattern
        Recebe eventos dos serviços e envia via WebSocket
        """
        try:
            message = {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'source': subject.__class__.__name__
            }
            
            if event_type.startswith('weather'):
                self._handle_weather_event(message)
            elif event_type.startswith('agro'):
                self._handle_agro_event(message)
            else:
                self._broadcast_general_event(message)
                
        except Exception as e:
            self.logger.error(f"Error handling update in WebSocketService: {e}")
    
    def _handle_weather_event(self, message):
        """Handle weather-related events"""
        self.socketio.emit('weather_update', message, broadcast=True)
        print(f"🌤️  Weather event broadcasted: {message['event_type']}")
    
    def _handle_agro_event(self, message):
        """Handle agricultural events"""
        self.socketio.emit('agro_update', message, broadcast=True)
        print(f"🌾 Agro event broadcasted: {message['event_type']}")
    
    def _broadcast_general_event(self, message):
        """Handle general events"""
        self.socketio.emit('general_update', message, broadcast=True)
        print(f"📢 General event broadcasted: {message['event_type']}")
    
    def on_connect(self, client_id: str):
        """Handle client connection"""
        self.connected_clients.add(client_id)
        self.client_subscriptions[client_id] = set()
        
        print(f"✅ Client connected: {client_id} (Total: {len(self.connected_clients)})")
        
        welcome_data = {
            'type': 'connection_established',
            'client_id': client_id,
            'timestamp': datetime.now().isoformat(),
            'message': 'Connected to FarmVille real-time updates'
        }
        
        self.socketio.emit('connection_status', welcome_data, room=client_id)
        
        if len(self.connected_clients) == 1:
            self.start_background_updates()
    
    def on_disconnect(self, client_id: str):
        """Handle client disconnection"""
        self.connected_clients.discard(client_id)
        self.client_subscriptions.pop(client_id, None)
        
        print(f"❌ Client disconnected: {client_id} (Remaining: {len(self.connected_clients)})")
        
        if len(self.connected_clients) == 0:
            self.stop_background_updates()
    
    def subscribe_to_terrain(self, client_id: str, terrain_id: str):
        """Subscribe client to specific terrain updates"""
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].add(terrain_id)
            print(f"📍 Client {client_id} subscribed to terrain {terrain_id}")
    
    def unsubscribe_from_terrain(self, client_id: str, terrain_id: str):
        """Unsubscribe client from terrain updates"""
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(terrain_id)
            print(f"📍 Client {client_id} unsubscribed from terrain {terrain_id}")
    
    def send_weather_alert(self, location: str, alert_type: str, message: str, priority: str = "medium"):
        """
        Envia alerta meteorológico urgente
        
        Args:
            location: Localização do alerta
            alert_type: Tipo de alerta (ex: 'storm', 'frost', 'heat_wave')
            message: Mensagem do alerta
            priority: Prioridade (low, medium, high, urgent)
        """
        alert_data = {
            'type': 'weather_alert',
            'location': location,
            'alert_type': alert_type,
            'message': message,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('weather_alert', alert_data, broadcast=True)
        print(f"🚨 Weather alert sent: {alert_type} for {location}")
    
    def send_agro_suggestion_update(self, terrain_id: str, suggestions: list, priority: str):
        """
        Envia atualização de sugestões agrícolas
        
        Args:
            terrain_id: ID do terreno
            suggestions: Lista de sugestões
            priority: Prioridade das sugestões
        """
        update_data = {
            'type': 'agro_suggestion_update',
            'terrain_id': terrain_id,
            'suggestions': suggestions,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        }
        
        for client_id, subscriptions in self.client_subscriptions.items():
            if terrain_id in subscriptions:
                self.socketio.emit('agro_update', update_data, room=client_id)
        
        print(f"🌾 Agro suggestion update sent for terrain {terrain_id}")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do WebSocket service"""
        return {
            'connected_clients': len(self.connected_clients),
            'total_subscriptions': sum(len(subs) for subs in self.client_subscriptions.values()),
            'background_thread_active': self._background_thread and self._background_thread.is_alive(),
            'clients': list(self.connected_clients)
        }


# WebSocket event handlers (para usar com Flask-SocketIO)
def setup_websocket_handlers(socketio: SocketIO, websocket_service: WebSocketService):
    """
    Configura handlers de eventos WebSocket
    
    Args:
        socketio: Instância do Flask-SocketIO
        websocket_service: Instância do WebSocketService
    """
    
    @socketio.on('connect')
    def handle_connect():
        client_id = request.sid
        websocket_service.on_connect(client_id)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        client_id = request.sid
        websocket_service.on_disconnect(client_id)
    
    @socketio.on('subscribe_terrain')
    def handle_subscribe_terrain(data):
        client_id = request.sid
        terrain_id = data.get('terrain_id')
        if terrain_id:
            websocket_service.subscribe_to_terrain(client_id, terrain_id)
            emit('subscription_confirmed', {'terrain_id': terrain_id})
    
    @socketio.on('unsubscribe_terrain')
    def handle_unsubscribe_terrain(data):
        client_id = request.sid
        terrain_id = data.get('terrain_id')
        if terrain_id:
            websocket_service.unsubscribe_from_terrain(client_id, terrain_id)
            emit('unsubscription_confirmed', {'terrain_id': terrain_id})
    
    @socketio.on('request_weather_update')
    def handle_weather_update_request(data):
        """Handle manual weather update requests"""
        terrain_id = data.get('terrain_id')
        if terrain_id:
            # Trigger immediate weather update
            emit('weather_update_triggered', {'terrain_id': terrain_id})
            print(f"🔄 Manual weather update requested for terrain {terrain_id}")
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping/pong for connection testing"""
        emit('pong', {'timestamp': datetime.now().isoformat()})
    
    print("🔌 WebSocket handlers configured")