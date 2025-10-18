from flask import Flask
from config import SECRET_KEY
from services.db import init_db

from routes.main import main
from routes.verify import verify
from routes.stats import stats
from routes.download import download

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Registrar Blueprints
app.register_blueprint(main)
app.register_blueprint(verify)
app.register_blueprint(stats)
app.register_blueprint(download)

# Inicializar base de datos
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)