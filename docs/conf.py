import os, sys
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
html_js_files = ['toggle.js']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
}