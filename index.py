
from flask import Flask, render_template_string, request, send_file, session, redirect, url_for
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime



app = Flask(__name__)

# Lista de conjuntos de preguntas
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
        'p1': ("¿Qué es un algoritmo?", ["Una secuencia de pasos", "Un tipo de hardware"], 'a'),
        'p2': ("¿Qué significa URL?", ["Uniform Resource Locator", "Universal Remote Link"], 'a'),
        'p3': ("¿Qué es un byte?", ["Unidad de almacenamiento", "Unidad de velocidad"], 'a')
    }
]

# Contador de conjunto actual
contador = {'index': 0}

def generar_formulario_html(preguntas):
    html = """
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <title>Casa Abierta - Informática</title>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
      <style>
        body {
          background: linear-gradient(to right, #e3f2fd, #ffffff);
        }
        .card {
          border-radius: 1rem;
        }
        .btn-custom {
          background-color: #0d6efd;
          color: white;
        }
        .btn-custom:hover {
          background-color: #0b5ed7;
        }
      </style>
    </head>
    <body>
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <div class="card shadow">
            <div class="card-header bg-primary text-white text-center">
              <h3 class="mb-0">Registro y Cuestionario de Informática</h3>
            </div>
            <div class="card-body">
              <form method="post">
                <div class="mb-3">
                  <label class="form-label">Nombre completo</label>
                  <input type="text" name="nombre" class="form-control" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Correo electrónico</label>
                  <input type="email" name="correo" class="form-control">
                </div>
                <div class="mb-3">
                  <label class="form-label">Institución</label>
                  <input type="text" name="institucion" class="form-control">
                </div>
                <hr>
                <h5 class="text-primary">Cuestionario</h5>
    """
    for i, (key, (pregunta, opciones, _)) in enumerate(preguntas.items(), start=1):
        html += f"""
        <div class="mb-3">
          <label class="form-label">{i}. {pregunta}</label>
        """
        for j, opcion in zip(['a', 'b'], opciones):
            html += f"""
            <div class="form-check">
              <input class="form-check-input" type="radio" name="{key}" value="{j}" required>
              <label class="form-check-label">{opcion}</label>
            </div>
            """
        html += "</div>"
    html += """
                <div class="text-center">
                  <button type="submit" class="btn btn-custom px-4">Enviar y generar certificado</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    </body>
    </html>
    """
    return html

def calcular_puntaje(respuestas, preguntas):
    return sum(1 for k in preguntas if respuestas.get(k) == preguntas[k][2])

def generar_certificado(nombre, puntaje, fecha):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(letter[0], letter[1] / 2))  # Media página

    # Fondo suave
    c.setFillColorRGB(0.95, 0.95, 1)
    c.rect(0, 0, letter[0], letter[1] / 2, fill=1)

    # Bordes decorativos
    c.setStrokeColor(colors.lightblue)
    c.setLineWidth(4)
    c.rect(20, 20, letter[0] - 40, (letter[1] / 2) - 40)

    # Título
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 60, "Certificado de Participación")

    # Contenido
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 90,
                        f"Se certifica que {nombre} ha participado en la Casa Abierta de Informática.")
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 110,
                        f"Puntaje obtenido en el cuestionario: {puntaje} / 3")
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 130,
                        f"Fecha de participación: {fecha}")
    c.drawCentredString(letter[0] / 2, (letter[1] / 2) - 160,
                        "¡Gracias por tu participación!")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

app.secret_key = 'tu_clave_secreta'  # Necesario para usar session

@app.route('/gracias')
def gracias():
    nombre = session.get('nombre')
    puntaje = session.get('puntaje')
    fecha = session.get('fecha')

    if not nombre:
        return redirect(url_for('index'))

    pdf = generar_certificado(nombre, puntaje, fecha)
    session['pdf'] = pdf.getvalue()

    # Eliminar datos de sesión para evitar reenvíos o accesos posteriores
    session.pop('nombre', None)
    session.pop('puntaje', None)
    session.pop('fecha', None)

    html = f"""
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <title>Gracias por participar</title>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body>
      <div class="container py-5 text-center">
        <h2 class="text-success">¡Gracias por participar, {nombre}!</h2>
        <p>Tu puntaje fue <strong>{puntaje} / 3</strong>.</p>
        <p>Fecha de participación: {fecha}</p>
        <a href="/descargar_certificado" class="btn btn-primary mt-3">Descargar certificado</a>
      </div>
      <script>
        window.history.pushState(null, "", window.location.href);
        window.onpopstate = function () {{
          window.history.pushState(null, "", window.location.href);
        }};
      </script>
    </body>
    </html>
    """
    return html
    nombre = session.get('nombre')
    puntaje = session.get('puntaje')
    fecha = session.get('fecha')

    if not nombre:
        return redirect(url_for('index'))

    pdf = generar_certificado(nombre, puntaje, fecha)
    session['pdf'] = pdf.getvalue()  # Guardar el PDF en sesión temporalmente

    html = f"""
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <title>Gracias por participar</title>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body>
      <div class="container py-5 text-center">
        <h2 class="text-success">¡Gracias por participar, {nombre}!</h2>
        <p>Tu puntaje fue <strong>{puntaje} / 3</strong> en el cuestionario.</p>
        <p>Fecha de participación: {fecha}</p>
        <a href="/descargar_certificado" class="btn btn-primary mt-3">Descargar certificado</a>
      </div>

      <script>
        window.history.pushState(null, "", window.location.href);
        window.onpopstate = function () {{
          window.history.pushState(null, "", window.location.href);
        }};
      </script>
    </body>
    </html>
    """
    return html

@app.route('/', methods=['GET', 'POST'])
def index():
    preguntas_actuales = conjuntos_preguntas[contador['index']]
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form.get('correo', '')
        institucion = request.form.get('institucion', '')
        respuestas = {k: request.form.get(k) for k in preguntas_actuales}
        puntaje = calcular_puntaje(respuestas, preguntas_actuales)
        fecha = datetime.now().strftime("%d/%m/%Y")

        conn = sqlite3.connect('participantes.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participantes (
                nombre TEXT, correo TEXT, institucion TEXT, puntaje INTEGER, fecha TEXT
            )
        """)
        cursor.execute("INSERT INTO participantes VALUES (?, ?, ?, ?, ?)",
                       (nombre, correo, institucion, puntaje, fecha))
        conn.commit()
        conn.close()

        contador['index'] = (contador['index'] + 1) % len(conjuntos_preguntas)

        # Guardar datos en sesión para usarlos en la página de agradecimiento
        session['nombre'] = nombre
        session['puntaje'] = puntaje
        session['fecha'] = fecha

        return redirect(url_for('gracias'))

    return render_template_string(generar_formulario_html(preguntas_actuales))

@app.route('/descargar_certificado')
def descargar_certificado():
    pdf_data = session.get('pdf')
    if not pdf_data:
        return redirect(url_for('index'))
    return send_file(BytesIO(pdf_data), as_attachment=True,
                     download_name='certificado.pdf', mimetype='application/pdf')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
