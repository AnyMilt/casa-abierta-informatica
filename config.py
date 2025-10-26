import os
import secrets

# Generar una clave secreta segura si no existe
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
DATABASE = 'participantes.db'