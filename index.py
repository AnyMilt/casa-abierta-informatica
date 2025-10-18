from flask import Flask, render_template_string, request, send_file, session, redirect, url_for
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import random
import os
from reportlab.platypus import Image
import matplotlib.pyplot as plt
import base64
import qrcode
import hashlib
import socket
from reportlab.lib.utils import ImageReader



app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_segura_por_defecto')

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
    },
    {
        'p1': ("¿Qué es software?", ["Parte física del computador", "Conjunto de programas"], 'b'),
        'p2': ("¿Qué es phishing?", ["Ataque para robar información", "Tipo de software educativo"], 'a'),
        'p3': ("¿Qué hace un antivirus?", ["Protege contra malware", "Mejora la velocidad de internet"], 'a')
    }
]

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

def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita conexión real, solo para obtener IP local
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def generar_formulario_html(preguntas):
    html = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
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
  <div class="container-fluid py-4">
    <div class="row justify-content-center">
      <div class="col-12 col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white text-center">
            <h3 class="mb-0">Registro y Cuestionario de Informática</h3>
          </div>
          <div class="card-body">
            <form method="post">
              <div class="mb-3">
                <label for="nombre" class="form-label">Nombre completo</label>
                <input type="text" id="nombre" name="nombre" class="form-control" required>
              </div>
              <div class="mb-3">
                <label for="correo" class="form-label">Correo electrónico</label>
                <input type="email" id="correo" name="correo" class="form-control">
              </div>
              <div class="mb-3">
                <label for="institucion" class="form-label">Institución</label>
                <input type="text" id="institucion" name="institucion" class="form-control" required>
              </div>
              <hr>
              <h5 class="text-primary">Cuestionario</h5>
    """

    for i, (key, (pregunta, opciones, _)) in enumerate(preguntas.items(), start=1):
        html += f"""<div class="mb-3">
        <label class="form-label">{i}. {pregunta}</label>"""
        for j, opcion in zip(map(chr, range(97, 97 + len(opciones))), opciones):
            input_id = f"{key}_{j}"
            html += f"""<div class="form-check">
              <input class="form-check-input" type="radio" name="{key}" value="{j}" id="{input_id}" required>
              <label class="form-check-label" for="{input_id}">{opcion}</label>
            </div>"""
        html += "</div>"

    html += """<div class="text-center">
                <button type="submit" class="btn btn-custom w-100 w-md-auto px-4">Enviar y generar certificado</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""
    return html

def calcular_puntaje(respuestas, preguntas):
    return sum(1 for k in preguntas if respuestas.get(k) == preguntas[k][2])

def generar_certificado_html(nombre, puntaje, fecha, codigo):
    ip_local = obtener_ip_local()
    qr_url = f"http://{ip_local}:5000/verificar_premio?codigo={codigo}"
    qr_img = qrcode.make(qr_url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()

    html = f"""
<!doctype html>
<html lang='es'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Certificado de Participación</title>
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
    <style>
        body {{
            background: linear-gradient(to right, #e3f2fd, #ffffff);
            font-family: 'Segoe UI', sans-serif;
            padding: 20px;
        }}
        .certificado {{
            max-width: 700px;
            margin: auto;
            padding: 20px;
            border: 3px solid #0d6efd;
            border-radius: 15px;
            background-color: #ffffff;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
        }}
        .certificado h2 {{
            color: #0d6efd;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}
        .certificado p {{
            font-size: 1rem;
            margin: 8px 0;
        }}
        .qr img {{
            margin-top: 20px;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 5px;
            background-color: #f8f9fa;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class='certificado text-center'>
        <h2>🎓 Certificado de Participación</h2>
        <p><strong>Nombre:</strong> {nombre}</p>
        <p><strong>Puntaje:</strong> {puntaje} / 3</p>
        <p><strong>Fecha:</strong> {fecha}</p>
        <p><strong>Código de verificación:</strong> {codigo}</p>
        <div class='qr'>
            <img src='data:image/png;base64,{qr_base64}' alt='Código QR'>
        </div>
        <p class='mt-4 text-success'>¡Gracias por tu participación en la Casa Abierta de Informática!</p>
    </div>
</body>
</html>
"""
    
    return html

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        preguntas_actuales = random.choice(conjuntos_preguntas)
        session['preguntas'] = preguntas_actuales
        return render_template_string(generar_formulario_html(preguntas_actuales))

    if request.method == 'POST':
      preguntas_actuales = session.get('preguntas')
      if not preguntas_actuales:
          return redirect(url_for('index'))

      nombre = request.form['nombre'].upper()
      correo = request.form.get('correo', '')
      institucion = request.form.get('institucion', '')
      respuestas = {k: request.form.get(k) for k in preguntas_actuales}
      puntaje = calcular_puntaje(respuestas, preguntas_actuales)
      fecha = datetime.now().strftime("%d/%m/%Y")
      codigo = hashlib.md5(f"{nombre}{fecha}".encode()).hexdigest()[:8]

      conn = sqlite3.connect('participantes.db')
      cursor = conn.cursor()
      cursor.execute("""
      INSERT INTO participantes (nombre, correo, institucion, puntaje, fecha, codigo, premio_entregado)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      """, (nombre, correo, institucion, puntaje, fecha, codigo, 0))
      conn.commit()
      conn.close()

      session.pop('preguntas', None)

      if puntaje >= 2:
          return generar_certificado_html(nombre, puntaje, fecha, codigo)
      else:
          return f"""<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
          <style>body {{ font-family: sans-serif; padding: 1rem; text-align: center; }}</style></head><body>
          <h2>¡Gracias por participar, {nombre}!</h2>
          <p>Tu puntaje fue <strong>{puntaje} / 3</strong>.</p>
          <p>No alcanzaste el puntaje mínimo para obtener certificado.</p>
          </body></html>"""
@app.route('/verificar_premio')
def verificar_premio():
    codigo = request.args.get('codigo', '').strip()
    if not codigo or len(codigo) < 5:
        return render_html("Código no válido.", "https://example.com/imagen_codigo_invalido.png")

    fecha = datetime.now().strftime("%d/%m/%Y")

    try:
        with sqlite3.connect('participantes.db') as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT nombre, premio_entregado 
                FROM participantes 
                WHERE codigo = ?
            """, (codigo,))
            resultado = cursor.fetchone()

            if resultado:
                nombre, entregado = resultado
                if entregado:
                    mensaje = f"🎉 El premio ya fue entregado a <strong>{nombre}</strong>."
                    imagen_url = "https://example.com/imagen_premio_entregado.png"
                else:
                    cursor.execute("""
                        UPDATE participantes 
                        SET premio_entregado = 1 
                        WHERE codigo = ?
                    """, (codigo,))
                    conn.commit()
                    mensaje = f"✅ Premio entregado correctamente a <strong>{nombre}</strong>."
                    imagen_url = "https://example.com/imagen_premio_nuevo.png"
            else:
                cursor.execute("""
                    INSERT INTO participantes 
                    (nombre, correo, institucion, puntaje, fecha, codigo, premio_entregado) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("DESCONOCIDO", "", "", 0, fecha, codigo, 1))
                conn.commit()
                mensaje = "🆕 Código no registrado previamente. Se ha creado un nuevo registro con premio entregado."
                imagen_url = "https://example.com/imagen_registro_nuevo.png"

    except sqlite3.Error as e:
        mensaje = f"❌ Error en la base de datos: {e}"
        imagen_url = "https://example.com/imagen_error.png"

    return render_html(mensaje, imagen_url)

def render_html(mensaje, imagen_url):
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f9f9f9;
                text-align: center;
                padding: 5vw;
            }}
            .mensaje {{
                font-size: 5vw;
                color: #333;
                margin-top: 4vh;
            }}
            .imagen {{
                max-width: 80%;
                height: auto;
                margin-top: 5vh;
                border-radius: 10px;
            }}
            @media (min-width: 768px) {{
                .mensaje {{
                    font-size: 28px;
                }}
                .imagen {{
                    max-width: 220px;
                }}
            }}
        </style>
    </head>
    <body>
        <img src="{imagen_url}" alt="Resultado" class="imagen"/>
        <div class="mensaje">{mensaje}</div>
    </body>
    </html>
    """

@app.route('/gracias')
def gracias():
    nombre = session.get('nombre')
    puntaje = session.get('puntaje')
    fecha = session.get('fecha')

    if not nombre:
        return redirect(url_for('index'))

    # Solo generar certificado si el puntaje es suficiente
    if puntaje >= 2:
        pdf = generar_certificado(nombre, puntaje, fecha)
        session['pdf'] = pdf.getvalue()
        certificado_html = "<a href='/descargar_certificado' class='btn btn-primary mt-3'>Descargar certificado</a>"
    else:
        certificado_html = "<p class='text-danger'>No alcanzaste el puntaje mínimo para obtener certificado.</p>"

    # Limpiar datos de sesión
    session.pop('nombre', None)
    session.pop('puntaje', None)
    session.pop('fecha', None)

    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
    <title>Gracias por participar</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head><body><div class="container py-5 text-center">
    <h2 class="text-success">¡Gracias por participar, {nombre}!</h2>
    <p>Tu puntaje fue <strong>{puntaje} / 3</strong>.</p>
    <p>Fecha de participación: {fecha}</p>
    {certificado_html}
    </div><script>
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function () {{ window.history.pushState(null, "", window.location.href); }};
    </script></body></html>"""
    return html

@app.route('/descargar_certificado')
def descargar_certificado():
    pdf_data = session.get('pdf')
    if not pdf_data:
        return redirect(url_for('index'))
    return send_file(BytesIO(pdf_data), as_attachment=True,
                     download_name='certificado.pdf', mimetype='application/pdf')


@app.route('/estadisticas')
def estadisticas():
    conn = sqlite3.connect('participantes.db')
    cursor = conn.cursor()

    cursor.execute("SELECT puntaje, COUNT(*) FROM participantes GROUP BY puntaje")
    datos = cursor.fetchall()
    conn.close()

    # Preparar datos
    puntajes = [str(p) for p, _ in datos]
    cantidades = [c for _, c in datos]

    # Crear gráfico
    fig, ax = plt.subplots()
    ax.bar(puntajes, cantidades, color='skyblue')
    ax.set_title('Distribución de Puntajes')
    ax.set_xlabel('Puntaje')
    ax.set_ylabel('Cantidad de Participantes')

    # Guardar imagen en memoria
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Mostrar en HTML
    img_base64 = base64.b64encode(img.getvalue()).decode()
    html = f"""<!doctype html><html><head><title>Estadísticas</title></head><body>
    <h2>Distribución de Puntajes</h2>
    <img src="data:image/png;base64,{img_base64}" alt="Gráfico de puntajes">
    </body></html>"""
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)