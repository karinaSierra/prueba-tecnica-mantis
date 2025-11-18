"""
Wrapper para Vercel Serverless Functions
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la aplicación Flask
from app import app

# Vercel espera el handler 'handler' o el objeto 'app'
handler = app

