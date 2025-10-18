import sqlite3
from config import DATABASE

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS participantes (
            nombre TEXT, correo TEXT, institucion TEXT,
            puntaje INTEGER, fecha TEXT, codigo TEXT,
            premio_entregado INTEGER
        )
        """)
        conn.commit()

def insert_participant(nombre, correo, institucion, puntaje, fecha, codigo):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO participantes (nombre, correo, institucion, puntaje, fecha, codigo, premio_entregado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, correo, institucion, puntaje, fecha, codigo, 0))
        conn.commit()

def get_participant_by_code(codigo):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, premio_entregado FROM participantes WHERE codigo = ?", (codigo,))
        return cursor.fetchone()

def mark_prize_delivered(codigo):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE participantes SET premio_entregado = 1 WHERE codigo = ?", (codigo,))
        conn.commit()

def create_unknown_participant(codigo, fecha):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO participantes (nombre, correo, institucion, puntaje, fecha, codigo, premio_entregado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("DESCONOCIDO", "", "", 0, fecha, codigo, 1))
        conn.commit()

def get_score_distribution():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT puntaje, COUNT(*) FROM participantes GROUP BY puntaje")
        return cursor.fetchall()