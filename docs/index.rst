Documentacao da API FarmVille
==============================

.. raw:: html

   <style>
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
   
   :root {
       --verde-primario: #2E8B57;
       --verde-secundario: #3CB371;
       --verde-claro: #90EE90;
       --verde-escuro: #228B22;
       --dourado: #DAA520;
       --amarelo-sol: #FFD700;
       --azul-ceu: #87CEEB;
       --branco: #ffffff;
       --cinza-claro: #f8f9fa;
       --cinza-escuro: #343a40;
   }
   
   body { font-family: 'Inter', sans-serif !important; }
   
   .wy-nav-top { 
       background: linear-gradient(135deg, var(--verde-primario) 0%, var(--verde-secundario) 100%) !important;
       border-bottom: 3px solid var(--dourado) !important;
   }
   
   .wy-nav-side { 
       background: linear-gradient(180deg, var(--verde-claro) 0%, var(--verde-primario) 100%) !important;
   }
   
   .rst-content h1 {
       color: var(--verde-primario) !important;
       font-family: 'Poppins', sans-serif !important;
       font-size: 2.5em !important;
       border-bottom: 3px solid var(--dourado) !important;
       padding-bottom: 10px !important;
   }
   
   .rst-content h2 {
       color: var(--verde-secundario) !important;
       font-family: 'Poppins', sans-serif !important;
       background: linear-gradient(90deg, rgba(46, 139, 87, 0.1) 0%, transparent 100%) !important;
       padding: 15px 20px !important;
       border-left: 4px solid var(--verde-primario) !important;
       border-radius: 0 8px 8px 0 !important;
   }
   
   .rst-content h3 {
       color: var(--verde-escuro) !important;
       font-family: 'Poppins', sans-serif !important;
   }
   
   .metodos-lista {
       background: linear-gradient(135deg, rgba(46, 139, 87, 0.05) 0%, rgba(144, 238, 144, 0.02) 100%);
       border: 1px solid rgba(46, 139, 87, 0.2);
       border-left: 4px solid var(--verde-primario);
       border-radius: 8px;
       padding: 20px;
       margin: 20px 0;
   }
   
   .metodos-lista ul {
       list-style: none;
       padding: 0;
   }
   
   .metodos-lista li {
       background: white;
       margin: 10px 0;
       padding: 15px;
       border-radius: 6px;
       border-left: 3px solid var(--verde-secundario);
       box-shadow: 0 2px 5px rgba(0,0,0,0.1);
       transition: all 0.3s ease;
   }
   
   .metodos-lista li:hover {
       transform: translateX(5px);
       box-shadow: 0 4px 10px rgba(0,0,0,0.15);
   }
   
   .metodo-nome {
       font-family: 'JetBrains Mono', monospace;
       font-weight: bold;
       color: var(--verde-escuro);
       font-size: 1.1em;
   }
   
   .metodo-desc {
       color: var(--cinza-escuro);
       margin-top: 5px;
       font-style: italic;
   }
   
   .highlight {
       border-left: 4px solid var(--verde-primario) !important;
       border-radius: 8px !important;
       background: var(--cinza-claro) !important;
   }
   </style>

🌾 **Bem-vindos a API FarmVille** - Plataforma de Gestao Agricola

Funcionalidades
---------------
* 🌤️ Dados meteorologicos em tempo real
* 🤖 Recomendacoes agricolas com IA
* 🌱 Gestao de terrenos
* 🔐 Autenticacao segura

Inicio Rapido
-------------

1. **Instalar dependencias:**

   .. code-block:: bash

      pip install -r requirements.txt

2. **Configurar ambiente:**

   .. code-block:: bash

      copy .env.example .env

3. **Iniciar aplicacao:**

   .. code-block:: bash

      python api_gateway.py

Arquitectura do Projecto
------------------------

O projecto FarmVille esta organizado da seguinte forma:

.. code-block:: text

   farmville/
   ├── api/                    # Rotas da API
   │   └── routes/            # Handlers das rotas
   ├── services/              # Logica de negocio
   ├── models/                # Modelos de dados
   ├── database/              # Camada de dados
   ├── utils/                 # Utilitarios
   └── tests/                 # Testes

Servicos Principais
-------------------

Weather Service
~~~~~~~~~~~~~~~

Servico responsavel por obter dados meteorologicos com integracao OpenWeatherMap API, cache inteligente e suporte para multiplas localizacoes.

.. raw:: html

   <div class="metodos-lista">
   <h4>🌤️ Principais Métodos:</h4>
   <ul>
       <li>
           <div class="metodo-nome">get_weather_data(location, lat, lon)</div>
           <div class="metodo-desc">Obtém dados meteorológicos para uma localização específica</div>
       </li>
       <li>
           <div class="metodo-nome">get_multiple_locations_concurrent(locations)</div>
           <div class="metodo-desc">Obtém dados para múltiplas localizações usando threading</div>
       </li>
       <li>
           <div class="metodo-nome">clear_cache()</div>
           <div class="metodo-desc">Limpa o cache de dados meteorológicos</div>
       </li>
       <li>
           <div class="metodo-nome">test_api_connection()</div>
           <div class="metodo-desc">Testa a conexão com a API OpenWeatherMap</div>
       </li>
   </ul>
   </div>

Agro Service
~~~~~~~~~~~~

Servico de inteligencia agricola com IA, integração OpenAI GPT, analise baseada em dados meteorologicos e sistema de confianca.

.. raw:: html

   <div class="metodos-lista">
   <h4>🤖 Principais Métodos:</h4>
   <ul>
       <li>
           <div class="metodo-nome">analyze_weather_for_agriculture(weather_data)</div>
           <div class="metodo-desc">Análise completa com IA baseada em dados meteorológicos</div>
       </li>
       <li>
           <div class="metodo-nome">get_simple_suggestions(temp, humidity, desc, location)</div>
           <div class="metodo-desc">Sugestões rápidas com parâmetros manuais</div>
       </li>
       <li>
           <div class="metodo-nome">get_suggestions_for_locations(weather_list)</div>
           <div class="metodo-desc">Análise em lote para múltiplas localizações</div>
       </li>
       <li>
           <div class="metodo-nome">clear_cache()</div>
           <div class="metodo-desc">Limpa o cache de sugestões agrícolas</div>
       </li>
   </ul>
   </div>

User Service
~~~~~~~~~~~~

Gestao de utilizadores e autenticacao com JWT, hash de passwords com salt e gestao de sessoes.

.. raw:: html

   <div class="metodos-lista">
   <h4>👤 Principais Métodos:</h4>
   <ul>
       <li>
           <div class="metodo-nome">register_user(username, password, email)</div>
           <div class="metodo-desc">Regista um novo utilizador no sistema</div>
       </li>
       <li>
           <div class="metodo-nome">login_user(username, password)</div>
           <div class="metodo-desc">Autentica utilizador e retorna token JWT</div>
       </li>
       <li>
           <div class="metodo-nome">get_user_from_token(token)</div>
           <div class="metodo-desc">Valida token e retorna informações do utilizador</div>
       </li>
       <li>
           <div class="metodo-nome">verify_token(token)</div>
           <div class="metodo-desc">Verifica se um token JWT é válido</div>
       </li>
   </ul>
   </div>

Terrain Service
~~~~~~~~~~~~~~~

Gestao de terrenos agricolas com operacoes CRUD, validacao de coordenadas GPS e integracao com servicos meteorologicos.

.. raw:: html

   <div class="metodos-lista">
   <h4>🌱 Principais Métodos:</h4>
   <ul>
       <li>
           <div class="metodo-nome">create_terrain(user_id, name, lat, lon, ...)</div>
           <div class="metodo-desc">Cria um novo terreno para o utilizador</div>
       </li>
       <li>
           <div class="metodo-nome">get_user_terrains(user_id)</div>
           <div class="metodo-desc">Obtém todos os terrenos de um utilizador</div>
       </li>
       <li>
           <div class="metodo-nome">update_terrain(terrain_id, user_id, updates)</div>
           <div class="metodo-desc">Actualiza informações de um terreno</div>
       </li>
       <li>
           <div class="metodo-nome">delete_terrain(terrain_id, user_id)</div>
           <div class="metodo-desc">Remove um terreno do sistema</div>
       </li>
       <li>
           <div class="metodo-nome">get_terrain_stats(user_id)</div>
           <div class="metodo-desc">Obtém estatísticas dos terrenos do utilizador</div>
       </li>
   </ul>
   </div>

Modelos de Dados
----------------

User
~~~~

Representa um utilizador do sistema:

* **username** - Nome de utilizador unico
* **email** - Email do utilizador  
* **password_hash** - Hash da password
* **created_at** - Data de criacao
* **last_login** - Ultimo login

WeatherData
~~~~~~~~~~~

Dados meteorologicos:

* **location** - Nome da localizacao
* **latitude/longitude** - Coordenadas GPS
* **temperature** - Temperatura em Celsius
* **humidity** - Humidade em percentagem
* **pressure** - Pressao atmosferica
* **description** - Descricao do tempo

Terrain
~~~~~~~

Terreno agricola:

* **name** - Nome do terreno
* **latitude/longitude** - Coordenadas
* **crop_type** - Tipo de cultura
* **area_hectares** - Area em hectares
* **notes** - Notas adicionais

AgroSuggestion
~~~~~~~~~~~~~~

Sugestoes agricolas geradas por IA:

* **suggestions** - Lista de sugestoes
* **priority** - Prioridade (low/medium/high/urgent)
* **confidence** - Nivel de confianca (0.0 a 1.0)
* **reasoning** - Explicacao das sugestoes

API Endpoints
-------------

Autenticacao
~~~~~~~~~~~~

.. raw:: html

   <div class="metodos-lista">
   <h4>🔐 Endpoints de Autenticação:</h4>
   <ul>
       <li>
           <div class="metodo-nome">POST /api/auth/register</div>
           <div class="metodo-desc">Registar novo utilizador</div>
       </li>
       <li>
           <div class="metodo-nome">POST /api/auth/login</div>
           <div class="metodo-desc">Login e obtenção de token</div>
       </li>
       <li>
           <div class="metodo-nome">GET /api/auth/profile</div>
           <div class="metodo-desc">Perfil do utilizador autenticado</div>
       </li>
   </ul>
   </div>

Meteorologia
~~~~~~~~~~~~

.. raw:: html

   <div class="metodos-lista">
   <h4>🌤️ Endpoints Meteorológicos:</h4>
   <ul>
       <li>
           <div class="metodo-nome">GET /api/weather/&lt;location&gt;</div>
           <div class="metodo-desc">Dados meteorológicos para localização específica</div>
       </li>
   </ul>
   </div>

Agricultura
~~~~~~~~~~~

.. raw:: html

   <div class="metodos-lista">
   <h4>🤖 Endpoints de IA Agrícola:</h4>
   <ul>
       <li>
           <div class="metodo-nome">POST /api/agro/analyze</div>
           <div class="metodo-desc">Análise agrícola completa com IA</div>
       </li>
       <li>
           <div class="metodo-nome">POST /api/agro/quick-analyze</div>
           <div class="metodo-desc">Análise rápida com dados manuais</div>
       </li>
       <li>
           <div class="metodo-nome">POST /api/agro/bulk-analyze</div>
           <div class="metodo-desc">Análise em lote para múltiplas localizações</div>
       </li>
   </ul>
   </div>

Terrenos
~~~~~~~~

.. raw:: html

   <div class="metodos-lista">
   <h4>🌱 Endpoints de Terrenos:</h4>
   <ul>
       <li>
           <div class="metodo-nome">POST /api/terrains</div>
           <div class="metodo-desc">Criar novo terreno</div>
       </li>
       <li>
           <div class="metodo-nome">GET /api/terrains</div>
           <div class="metodo-desc">Listar terrenos do utilizador</div>
       </li>
       <li>
           <div class="metodo-nome">GET /api/terrains/&lt;id&gt;</div>
           <div class="metodo-desc">Obter terreno específico</div>
       </li>
       <li>
           <div class="metodo-nome">PUT /api/terrains/&lt;id&gt;</div>
           <div class="metodo-desc">Actualizar terreno</div>
       </li>
       <li>
           <div class="metodo-nome">DELETE /api/terrains/&lt;id&gt;</div>
           <div class="metodo-desc">Remover terreno</div>
       </li>
   </ul>
   </div>

WebSocket Events
---------------

O sistema suporta actualizacoes em tempo real via WebSocket:

* **weather_update** - Actualizacoes meteorologicas
* **agro_update** - Novas sugestoes agricolas  
* **weather_alert** - Alertas meteorologicos urgentes

Configuracao
------------

Variaveis de Ambiente
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Base de dados
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=farmville
   POSTGRES_PASSWORD=farmville
   POSTGRES_DB=farmville

   # Autenticacao
   JWT_SECRET=your-secret-key

   # APIs externas
   OPENAI_API_KEY=your-openai-key
   OPENWEATHERMAP_API_KEY=your-weather-key

Instalacao
~~~~~~~~~~

.. code-block:: bash

   # Clonar repositorio
   git clone <url>
   cd farmville

   # Ambiente virtual
   python -m venv venv
   venv\Scripts\activate

   # Dependencias
   pip install -r requirements.txt

   # Base de dados
   docker-compose up -d

   # Configuracao
   copy .env.example .env

   # Iniciar
   python api_gateway.py

Testes
------

.. code-block:: bash

   # Executar todos os testes
   python -m pytest tests/ -v

   # Testes especificos
   python -m pytest tests/test_weather_service.py -v

Indices
=======

* :ref:`genindex`
* :ref:`search`