from flask import Blueprint, render_template
from services.db import get_score_distribution
import matplotlib.pyplot as plt
from io import BytesIO
import base64

stats = Blueprint('stats', __name__)

@stats.route('/estadisticas')
def estadisticas():
    datos = get_score_distribution()
    puntajes = [str(p) for p, _ in datos]
    cantidades = [c for _, c in datos]

    fig, ax = plt.subplots()
    ax.bar(puntajes, cantidades, color='skyblue')
    ax.set_title('Distribución de Puntajes')
    ax.set_xlabel('Puntaje')
    ax.set_ylabel('Cantidad de Participantes')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()

    html = f"""
    <!doctype html><html><head><title>Estadísticas</title></head><body>
    <h2>Distribución de Puntajes</h2>
    <img src="data:image/png;base64,{img_base64}" alt="Gráfico de puntajes">
    </body></html>
    """
    return html