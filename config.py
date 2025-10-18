import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_segura_por_defecto')
DATABASE = 'participantes.db'