from flask import Blueprint, request, jsonify, current_app
from api.routes.auth_routes import token_required

agro_bp = Blueprint('agro', __name__)

@agro_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_weather_for_agriculture(current_user):
    """
    Analisa dados meteorológicos e fornece sugestões agrícolas
    
    Args:
        current_user: Objeto do utilizador autenticado
        
    Corpo do Pedido:
        location (str): Nome da localização da quinta
        latitude (float): Coordenada de latitude
        longitude (float): Coordenada de longitude
        
    Returns:
        Resposta JSON com dados meteorológicos e sugestões agrícolas
    """
    try:
        # Obter dados do pedido
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados em falta"}), 400
        
        # Extrair parâmetros com valores por defeito
        location = data.get('location', 'Quinta')
        lat = float(data.get('latitude', 41.1579))
        lon = float(data.get('longitude', -8.6291))
        
        # Obter dados meteorológicos através do serviço
        weather_data = current_app.weather_service.get_weather_data(location, lat, lon)
        if not weather_data:
            return jsonify({
                "success": False,
                "error": "Não foi possível obter dados meteorológicos"
            }), 500
        
        # Gerar sugestões agrícolas baseadas no tempo
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
                "error": "Não foi possível gerar sugestões agrícolas"
            }), 500
            
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Dados de entrada inválidos: {str(e)}"
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
    Análise agrícola rápida com dados meteorológicos manuais
    
    Args:
        current_user: Objeto do utilizador autenticado
        
    Corpo do Pedido:
        temperature (float): Temperatura em Celsius
        humidity (float): Percentagem de humidade
        description (str): Descrição do tempo
        location (str): Nome da localização
        
    Returns:
        Resposta JSON com sugestões agrícolas
    """
    try:
        # Validar dados do pedido
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados em falta"}), 400
        
        # Extrair parâmetros meteorológicos
        temperature = float(data.get('temperature', 20))
        humidity = float(data.get('humidity', 60))
        description = data.get('description', 'Céu limpo')
        location = data.get('location', 'Quinta')
        
        # Gerar sugestões com dados simples (sem API meteorológica)
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
                "error": "Não foi possível gerar sugestões"
            }), 500
            
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Dados de entrada inválidos: {str(e)}"
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
    Analisa múltiplas localizações para insights agrícolas
    
    Args:
        current_user: Objeto do utilizador autenticado
        
    Corpo do Pedido:
        locations (list): Lista de objetos de localização com nome, latitude, longitude
        
    Returns:
        Resposta JSON com resultados de análise para todas as localizações
    """
    try:
        # Validar dados do pedido
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados em falta"}), 400
        
        # Obter lista de localizações
        locations = data.get('locations', [])
        if not locations:
            return jsonify({"error": "Nenhuma localização fornecida"}), 400
        
        # Recolher dados meteorológicos para cada localização
        weather_data_list = []
        for loc_data in locations:
            location = loc_data.get('name', 'Desconhecida')
            lat = float(loc_data.get('latitude', 0))
            lon = float(loc_data.get('longitude', 0))
            
            # Obter dados meteorológicos para esta localização
            weather = current_app.weather_service.get_weather_data(location, lat, lon)
            if weather:
                weather_data_list.append(weather)
        
        # Gerar sugestões para todas as localizações
        suggestions = current_app.agro_service.get_suggestions_for_locations(weather_data_list)
        
        return jsonify({
            "success": True,
            "analyzed_locations": len(suggestions),
            "suggestions": [sug.to_dict() for sug in suggestions]
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Dados de entrada inválidos: {str(e)}"
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
    Obtém informações do cache do serviço agrícola
    
    Args:
        current_user: Objeto do utilizador autenticado
        
    Returns:
        Resposta JSON com estatísticas do cache
    """
    # Obter informações do cache do serviço agrícola
    cache_info = current_app.agro_service.get_cache_info()
    return jsonify({
        "success": True,
        "cache_info": cache_info
    })

@agro_bp.route('/observer-stats', methods=['GET'])
@token_required
def get_observer_stats(current_user):
    """
    Obtém estatísticas do padrão observer para monitorização
    
    Args:
        current_user: Objeto do utilizador autenticado
        
    Returns:
        Resposta JSON com estatísticas do observer
    """
    # Isto precisaria de estar ligado à instância real do observer
    # Por agora, retorna estatísticas básicas
    return jsonify({
        "success": True,
        "observer_stats": {
            "total_events": 0,
            "event_breakdown": {}
        }
    })

@agro_bp.route('/analyze-by-parish', methods=['POST'])
@token_required
def analyze_by_parish(current_user):
    """
    Análise agrícola usando ID da freguesia portuguesa
    
    Args:
        current_user: Objeto do utilizador autenticado
        
    Corpo do Pedido:
        parish_id (int): ID da freguesia
        
    Returns:
        Resposta JSON com localização, tempo e sugestões agrícolas
    """
    try:
        # Validar dados do pedido
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados em falta"}), 400
        
        parish_id = data.get('parish_id')
        if not parish_id:
            return jsonify({
                "success": False,
                "error": "parish_id é obrigatório"
            }), 400
        
        # Obter localização através do serviço de localização
        location = current_app.location_service.get_location_from_parish(int(parish_id))
        if not location:
            return jsonify({
                "success": False,
                "error": "Localização não encontrada"
            }), 404
        
        if not location.has_coordinates():
            return jsonify({
                "success": False,
                "error": "Coordenadas não disponíveis para esta localização"
            }), 400
        
        # Obter dados meteorológicos
        weather_data = current_app.weather_service.get_weather_data(
            location.get_full_name(), 
            location.latitude, 
            location.longitude
        )
        
        if not weather_data:
            return jsonify({
                "success": False,
                "error": "Não foi possível obter dados meteorológicos"
            }), 500
        
        # Gerar análise agrícola
        suggestion = current_app.agro_service.analyze_weather_for_agriculture(weather_data)
        
        if not suggestion:
            return jsonify({
                "success": False,
                "error": "Não foi possível gerar sugestões agrícolas"
            }), 500
        
        return jsonify({
            "success": True,
            "location": location.to_dict(),
            "weather": weather_data.to_dict(),
            "agro_suggestions": suggestion.to_dict()
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Dados de entrada inválidos: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agro_bp.route('/analyze-user-terrains', methods=['GET'])
@token_required
def analyze_user_terrains(current_user):
    """
    Análise agrícola para todos os terrenos do utilizador
    
    Args:
        current_user: Objeto do utilizador autenticado
        
    Returns:
        Resposta JSON com análises para todos os terrenos do utilizador
    """
    try:
        # Obter terrenos do utilizador
        terrains_result = current_app.terrain_service.get_user_terrains(current_user['id'])
        
        if not terrains_result['success']:
            return jsonify({
                "success": False,
                "error": "Erro ao obter terrenos do utilizador"
            }), 400
        
        # Analisar cada terreno
        analyses = []
        for terrain in terrains_result['terrains']:
            if terrain.get('latitude') and terrain.get('longitude'):
                # Obter dados meteorológicos para este terreno
                weather = current_app.weather_service.get_weather_data(
                    terrain.get('name', 'Terreno'), 
                    terrain['latitude'], 
                    terrain['longitude']
                )
                
                # Gerar sugestões agrícolas
                suggestion = None
                if weather:
                    suggestion = current_app.agro_service.analyze_weather_for_agriculture(weather)
                
                analyses.append({
                    "terrain": terrain,
                    "weather": weather.to_dict() if weather else None,
                    "suggestions": suggestion.to_dict() if suggestion else None
                })
        
        return jsonify({
            "success": True,
            "total_terrains": len(terrains_result['terrains']),
            "analyzed_terrains": len(analyses),
            "terrain_analyses": analyses
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro na análise dos terrenos: {str(e)}"
        }), 500