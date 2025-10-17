
from flask import Flask, render_template_string, request, send_file
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<title>Casa Abierta - Informática</title>
<h2>Registro y Cuestionario</h2>
<form method="post">
  <label>Nombre:</label><br>
  <input type="text" name="nombre" required><br><br>
  <label>Correo:</label><br>
  <input type="email" name="correo"><br><br>
  <label>Institución:</label><br>
  <input type="text" name="institucion"><br><br>
  <h3>Cuestionario</h3>
  <label>1. ¿Qué significa CPU?</label><br>
  <input type="radio" name="p1" value="a"> Central Processing Unit<br>
  <input type="radio" name="p1" value="b"> Computer Personal Unit<br><br>

  <label>2. ¿Cuál es un sistema operativo?</label><br>
  <input type="radio" name="p2" value="a"> Microsoft Word<br>
  <input type="radio" name="p2" value="b"> Windows<br><br>

  <label>3. ¿Qué es HTML?</label><br>
  <input type="radio" name="p3" value="a"> Un lenguaje de programación<br>
  <input type="radio" name="p3" value="b"> Lenguaje de marcado para páginas web<br><br>

  <input type="submit" value="Enviar y generar certificado">
</form>
"""

def calcular_puntaje(respuestas):
    correctas = {'p1': 'a', 'p2': 'b', 'p3': 'b'}
    return sum(1 for k in correctas if respuestas.get(k) == correctas[k])

def generar_certificado(nombre, puntaje):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(300, 750, "Certificado de Participación")
    c.setFont("Helvetica", 14)
    c.drawString(100, 700, f"Se certifica que {nombre} ha participado en la Casa Abierta de Informática.")
    c.drawString(100, 670, f"Puntaje obtenido en el cuestionario: {puntaje} / 3")
    c.drawString(100, 640, "¡Gracias por tu participación!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        institucion = request.form['institucion']
        respuestas = {k: request.form.get(k) for k in ['p1', 'p2', 'p3']}
        puntaje = calcular_puntaje(respuestas)

        conn = sqlite3.connect('participantes.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS participantes
                          (nombre TEXT, correo TEXT, institucion TEXT, puntaje INTEGER)''')
        cursor.execute('INSERT INTO participantes VALUES (?, ?, ?, ?)',
                       (nombre, correo, institucion, puntaje))
        conn.commit()
        conn.close()

        pdf = generar_certificado(nombre, puntaje)
        return send_file(pdf, as_attachment=True, download_name='certificado.pdf', mimetype='application/pdf')

    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(debug=True)