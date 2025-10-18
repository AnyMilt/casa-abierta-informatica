import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(__file__), '..', 'participantes.db')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participantes (
            nombre TEXT,
            correo TEXT,
            institucion TEXT,
            puntaje INTEGER,
            fecha TEXT,
            codigo TEXT,
            premio_entregado INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente.")

if __name__ == '__main__':
    init_db()