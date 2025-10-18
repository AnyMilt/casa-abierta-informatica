import base64, hashlib, qrcode
from io import BytesIO
from datetime import datetime
from services.utils import get_local_ip
from flask import render_template

def generate_code(nombre, fecha):
    return hashlib.md5(f"{nombre}{fecha}".encode()).hexdigest()[:8]

def generate_certificate_html(nombre, puntaje, fecha, codigo):
    ip_local = get_local_ip()
    qr_url = f"http://{ip_local}:5000/verificar_premio?codigo={codigo}"
    qr_img = qrcode.make(qr_url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()

    return render_template('certificate.html', nombre=nombre, puntaje=puntaje, fecha=fecha, codigo=codigo, qr_base64=qr_base64)