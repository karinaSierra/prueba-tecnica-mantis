"""
Wrapper para Vercel Serverless Functions
Vercel Python runtime maneja Flask automáticamente
"""
import sys
import os

# Obtener el directorio raíz del proyecto
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Agregar al path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Cambiar al directorio raíz para que Flask encuentre templates y static
os.chdir(root_dir)

# Importar la aplicación Flask
from app import app

# Vercel Python runtime espera que exportemos la app Flask directamente
# El runtime maneja automáticamente la conversión WSGI a HTTP
handler = app
