#!/usr/bin/env python3
"""
Construtor Simples de Documentacao FarmVille

Um script minimalista e limpo para construir documentacao Sphinx bonita.
Uso: python build_docs.py [init|build|serve|clean]
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run(command, cwd=None):
    """Executa um comando e retorna True se bem-sucedido."""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def init_docs():
    """Inicializa a estrutura e ficheiros de documentacao."""
    print("A inicializar documentacao...")
    
    # Cria estrutura de diretorios
    Path("docs/_static").mkdir(parents=True, exist_ok=True)
    Path("docs/_templates").mkdir(exist_ok=True)
    
    # Cria conf.py minimalista
    with open("docs/conf.py", "w", encoding='utf-8') as f:
        f.write("""import os, sys
sys.path.insert(0, os.path.abspath('..'))

project = 'FarmVille API'
author = 'Equipa FarmVille'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode', 
    'sphinx.ext.napoleon',
]

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
}
""")
    
    # Cria CSS personalizado bonito
    with open("docs/_static/custom.css", "w", encoding='utf-8') as f:
        f.write(""":root {
    --verde: #4CAF50;
    --verde-escuro: #388E3C;
    --verde-claro: #81C784;
}

.wy-nav-top { background: var(--verde) !important; }
.wy-nav-side { background: linear-gradient(var(--verde-claro), var(--verde)); }
.wy-menu-vertical a { color: white !important; }
.wy-menu-vertical a:hover { background: var(--verde-escuro) !important; }

.highlight { border-left: 4px solid var(--verde); padding-left: 10px; }
.py.class > dt, .py.method > dt, .py.function > dt {
    background: rgba(76, 175, 80, 0.1) !important;
    border-left: 4px solid var(--verde) !important;
    padding: 8px 12px !important;
}
""")
    
    # Cria index.rst principal
    with open("docs/index.rst", "w", encoding='utf-8') as f:
        f.write("""Documentacao da API FarmVille
==============================

Bem-vindos a API FarmVille - Plataforma de Gestao Agricola

Funcionalidades
---------------
* Dados meteorologicos em tempo real
* Recomendacoes agricolas com IA
* Gestao de terrenos
* Autenticacao segura

Inicio Rapido
-------------

.. code-block:: bash

   pip install -r requirements.txt
   python api_gateway.py

Referencia da API
-----------------

Servicos
~~~~~~~~

.. automodule:: services.weather_service
   :members:

.. automodule:: services.agro_service
   :members:

.. automodule:: services.user_service
   :members:

.. automodule:: services.terrain_service
   :members:

Modelos
~~~~~~~

.. automodule:: models.weather_data
   :members:

.. automodule:: models.agro_data
   :members:

.. automodule:: models.user
   :members:

.. automodule:: models.terrain
   :members:

Indices
=======

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""")
    
    print("Documentacao inicializada!")

def build_docs():
    """Constroi a documentacao usando Python directamente."""
    print("A construir documentacao...")
    
    if not Path("docs").exists():
        print("Erro: Execute 'python build_docs.py init' primeiro")
        return False
    
    try:
        # Importa sphinx e constroi directamente
        from sphinx.cmd.build import main as sphinx_main
        
        # Cria directorio de build
        Path("docs/_build/html").mkdir(parents=True, exist_ok=True)
        
        # Muda para directorio docs
        original_dir = os.getcwd()
        os.chdir("docs")
        
        # Constroi documentacao
        result = sphinx_main(['-b', 'html', '.', '_build/html', '-q'])
        
        # Volta ao directorio original
        os.chdir(original_dir)
        
        if result == 0:
            print("Documentacao construida com sucesso!")
            html_path = Path("docs/_build/html/index.html").absolute()
            print(f"Abrir: {html_path}")
            return True
        else:
            print("Erro na construcao da documentacao")
            return False
            
    except ImportError:
        print("Erro: Sphinx nao esta instalado. Execute: pip install sphinx sphinx-rtd-theme")
        return False
    except Exception as e:
        print(f"Erro durante a construcao: {e}")
        return False

def serve_docs():
    """Serve a documentacao localmente."""
    html_dir = Path("docs/_build/html")
    
    if not html_dir.exists():
        print("Documentacao construida nao encontrada. Execute 'python build_docs.py build' primeiro")
        return
    
    print("A servir em http://localhost:8000")
    print("Prima Ctrl+C para parar")
    
    try:
        # Muda para directorio HTML
        original_dir = os.getcwd()
        os.chdir(html_dir)
        
        # Inicia servidor
        subprocess.run([sys.executable, "-m", "http.server", "8000"])
        
        # Volta ao directorio original
        os.chdir(original_dir)
        
    except KeyboardInterrupt:
        print("\nServidor parado")
    except Exception as e:
        print(f"Erro ao servir documentacao: {e}")

def open_docs():
    """Abre a documentacao no browser."""
    html_file = Path("docs/_build/html/index.html")
    
    if html_file.exists():
        import webbrowser
        webbrowser.open(f"file://{html_file.absolute()}")
        print("Documentacao aberta no browser")
    else:
        print("Documentacao nao encontrada. Execute 'python build_docs.py build' primeiro")

def clean_docs():
    """Limpa a documentacao construida."""
    build_dir = Path("docs/_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("Documentacao limpa")
    else:
        print("Nada para limpar")

def main():
    """Ponto de entrada principal."""
    commands = {
        'init': init_docs,
        'build': build_docs, 
        'serve': serve_docs,
        'open': open_docs,
        'clean': clean_docs,
    }
    
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print("""
Construtor de Documentacao FarmVille

Uso:
  python build_docs.py init     # Inicializa estrutura de documentacao
  python build_docs.py build    # Constroi documentacao HTML  
  python build_docs.py serve    # Serve documentacao em localhost:8000
  python build_docs.py open     # Abre documentacao no browser
  python build_docs.py clean    # Limpa ficheiros de construcao

Inicio rapido:
  python build_docs.py init
  python build_docs.py build
  python build_docs.py open
""")
        return
    
    commands[sys.argv[1]]()

if __name__ == "__main__":
    main()