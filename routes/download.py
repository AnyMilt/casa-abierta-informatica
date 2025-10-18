from flask import Blueprint, send_file, session, redirect, url_for, render_template
from io import BytesIO

download = Blueprint('download', __name__)

@download.route('/descargar_certificado')
def descargar_certificado():
    pdf_data = session.get('pdf')
    if not pdf_data:
        return redirect(url_for('main.index'))
    return send_file(BytesIO(pdf_data), as_attachment=True,
                     download_name='certificado.pdf', mimetype='application/pdf')