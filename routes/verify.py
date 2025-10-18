from flask import Blueprint, request, render_template
from datetime import datetime
from services.db import get_participant_by_code, mark_prize_delivered, create_unknown_participant

verify = Blueprint('verify', __name__)

@verify.route('/verificar_premio')
def verificar_premio():
    codigo = request.args.get('codigo', "").strip()
    if not codigo or len(codigo) < 5:
        return render_template('verify.html',
                               mensaje="Código no válido.",
                               imagen_url="https://example.com/imagen_codigo_invalido.png")

    fecha = datetime.now().strftime("%d/%m/%Y")
    resultado = get_participant_by_code(codigo)

    if resultado:
        nombre, entregado = resultado
        if entregado:
            mensaje = f"☑ El premio ya fue entregado a <strong>{nombre}</strong>."
            imagen_url = "https://example.com/imagen_premio_entregado.png"
        else:
            mark_prize_delivered(codigo)
            mensaje = f"🎉 Premio entregado correctamente a <strong>{nombre}</strong>."
            imagen_url = "https://example.com/imagen_premio_nuevo.png"
    else:
        create_unknown_participant(codigo, fecha)
        mensaje = "🆕 Código no registrado previamente. Se ha creado un nuevo registro con premio entregado."
        imagen_url = "https://example.com/imagen_registro_nuevo.png"

    return render_template('verify.html', mensaje=mensaje, imagen_url=imagen_url)