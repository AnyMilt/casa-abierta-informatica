import random

conjuntos_preguntas = [
    {
        'p1': ("¿Qué significa CPU?", ["Central Processing Unit", "Computer Personal Unit"], 'a'),
        'p2': ("¿Cuál es un sistema operativo?", ["Microsoft Word", "Windows"], 'b'),
        'p3': ("¿Qué es HTML?", ["Un lenguaje de programación", "Lenguaje de marcado para páginas web"], 'b')
    },
    {
        'p1': ("¿Qué significa RAM?", ["Random Access Memory", "Read Only Memory"], 'a'),
        'p2': ("¿Cuál es la función de un antivirus?", ["Acelerar el computador", "Proteger contra malware"], 'b'),
        'p3': ("¿Qué es un navegador web?", ["Un programa para editar texto", "Un programa para acceder a internet"], 'b')
    },
    {
        'p1': ("¿Qué significa USB?", ["Universal Serial Bus", "United Software Business"], 'a'),
        'p2': ("¿Cuál es la función del teclado?", ["Mostrar imágenes", "Introducir datos al computador"], 'b'),
        'p3': ("¿Qué es un archivo PDF?", ["Un documento de texto", "Un formato de documento portátil"], 'b')
    },
    {
        'p1': ("¿Qué significa WiFi?", ["Wireless Fidelity", "Wide File Internet"], 'a'),
        'p2': ("¿Cuál es la función del mouse?", ["Reproducir sonido", "Controlar el cursor en pantalla"], 'b'),
        'p3': ("¿Qué es un virus informático?", ["Un programa útil", "Un programa malicioso"], 'b')
    }
]

def get_random_questions():
    return random.choice(conjuntos_preguntas)

def calculate_score(respuestas, preguntas):
    return sum(1 for k in preguntas if respuestas.get(k) == preguntas[k][2])