from flask import Blueprint, send_file, session, redirect, url_for, render_template
from io import BytesIO

escanear = Blueprint('scanear', __name__)
@escanear.route('/scanear')
def scanear():
    return render_template('scan.html')