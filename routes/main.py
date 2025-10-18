from flask import Blueprint, render_template, request, session, redirect, url_for
from datetime import datetime
from services.quiz import get_random_questions, calculate_score
from services.db import insert_participant
from services.certificate import generate_code, generate_certificate_html

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        preguntas = get_random_questions()
        session['preguntas'] = preguntas
        return render_template('form.html', preguntas=preguntas)

    preguntas = session.get('preguntas')
    if not preguntas:
        return redirect(url_for('main.index'))

    nombre = request.form['nombre'].upper()
    correo = request.form.get('correo', "")
    institucion = request.form.get('institucion', "")
    respuestas = {k: request.form.get(k) for k in preguntas}
    puntaje = calculate_score(respuestas, preguntas)
    fecha = datetime.now().strftime("%d/%m/%Y")
    codigo = generate_code(nombre, fecha)

    insert_participant(nombre, correo, institucion, puntaje, fecha, codigo)
    session.pop('preguntas', None)

    if puntaje >= 2:
        return generate_certificate_html(nombre, puntaje, fecha, codigo)
    else:
        return render_template('result.html', nombre=nombre, puntaje=puntaje)