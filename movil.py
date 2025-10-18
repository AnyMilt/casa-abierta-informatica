from flask import Flask, render_template_string, request, send_file
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import random

app = Flask(__name__)

# Preguntas
conjuntos_preguntas = [
    {
        'p1': ("¿Qué significa CPU?", ["Central Processing Unit", "Computer Personal Unit"], 'a'),
        'p2': ("¿Cuál es un sistema operativo?", ["Microsoft Word", "Windows"], 'b'),
        'p3': ("¿Qué es HTML?", ["Un lenguaje de programación", "Lenguaje de marcado para páginas web"], 'b')
    },
    {
        'p1': ("¿Qué es RAM?", ["Memoria de acceso aleatorio", "Unidad de almacenamiento"], 'a'),
        'p2': ("¿Qué hace un navegador web?", ["Edita imágenes", "Accede a páginas web"], 'b'),
        'p3': ("¿Qué es un archivo PDF?", ["Formato de imagen", "Formato de documento portátil"], 'b')
    },
    {
        'p1': ("¿Qué es software?", ["Parte física del computador", "Conjunto de programas"], 'b'),
        'p2': ("¿Qué es phishing?", ["Ataque para robar información", "Tipo de software educativo"], 'a'),
        'p3': ("¿Qué hace un antivirus?", ["Protege contra malware", "Mejora la velocidad de internet"], 'a')
    }
]

# Inicializar base de datos
def inicializar_db():
    conn = sqlite3.connect('participantes.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participantes (
            nombre TEXT, correo TEXT, institucion TEXT, puntaje INTEGER, fecha TEXT
        )
    """)
    conn.commit()
    conn.close()

inicializar_db()

# Generar HTML móvil
def generar_formulario_html(preguntas):
    html = """<!doctype html><html lang="es"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Registro y Cuestionario</title>
    <style>
      body { font-family: sans-serif; background-color: #f0f8ff; padding: 1rem; }
      input, button { font-size: 1.2rem; padding: 0.75rem; margin-bottom: 1rem; width: 100%; }
      label { font-weight: bold; margin-top: 1rem; display: block; }
      .radio-group { margin-bottom: 1rem; }
    </style></head><body>
    <h2>Registro y Cuestionario</h2>
    <form method="post">
      <label>Nombre completo</label>
      <input type="text" name="nombre" required>
      <label>Correo electrónico</label>
      <input type="email" name="correo">
      <label>Institución</label>
      <input type="text" name="institucion">
      <hr>
      <h3>Cuestionario</h3>
    """
    for i, (key, (pregunta, opciones, _)) in enumerate(preguntas.items(), start=1):
        html += f"<label>{i}. {pregunta}</label>"
        for j, opcion in zip(['a', 'b'], opciones):
            html += f"""<div class="radio-group">
              <input type="radio" name="{key}" value="{j}" required> {opcion}
            </div>"""
    html += """<button type="submit">Enviar y generar certificado</button></form></body></html>"""
    return html

# Calcular puntaje
def calcular_puntaje(respuestas, preguntas):
    return sum(1 for k in preguntas if respuestas.get(k) == preguntas[k][2])

# Generar certificado PDF
def generar_certificado(nombre, puntaje, fecha):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(letter[0], letter[1] / 2))
    c.setFillColorRGB(0.95, 0.95, 1)
    c.rect(0, 0, letter[0], letter[1] / 2, fill=1)
    c.setStrokeColor(colors.lightblue)
    c.setLineWidth(4)
    c.rect(20, 20, letter[0] - 40, (letter[1] / 2) - 40)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 60, "Certificado de Participación")
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 90, f"{nombre} participó en la Casa Abierta de Informática.")
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 110, f"Puntaje: {puntaje} / 3")
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 130, f"Fecha: {fecha}")
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 160, "¡Gracias por tu participación!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    preguntas_actuales = random.choice(conjuntos_preguntas)
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form.get('correo', '')
        institucion = request.form.get('institucion', '')
        respuestas = {k: request.form.get(k) for k in preguntas_actuales}
        puntaje = calcular_puntaje(respuestas, preguntas_actuales)
        fecha = datetime.now().strftime("%d/%m/%Y")

        conn = sqlite3.connect('participantes.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO participantes VALUES (?, ?, ?, ?, ?)",
                       (nombre, correo, institucion, puntaje, fecha))
        conn.commit()
        conn.close()

        if puntaje >= 2:
            pdf = generar_certificado(nombre, puntaje, fecha)
            return send_file(pdf, as_attachment=True, download_name='certificado.pdf', mimetype='application/pdf')
        else:
            return f"""<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
            <style>body {{ font-family: sans-serif; padding: 1rem; text-align: center; }}</style></head><body>
            <h2>¡Gracias por participar, {nombre}!</h2>
            <p>Tu puntaje fue <strong>{puntaje} / 3</strong>.</p>
            <p>No alcanzaste el puntaje mínimo para obtener certificado.</p>
            </body></html>"""

    return render_template_string(generar_formulario_html(preguntas_actuales))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)