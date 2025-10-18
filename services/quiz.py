import random

conjuntos_preguntas = [
    {
        'p1': ("¿Qué significa CPU?", ["Central Processing Unit", "Computer Personal Unit"], 'a'),
        'p2': ("¿Cuál es un sistema operativo?", ["Microsoft Word", "Windows"], 'b'),
        'p3': ("¿Qué es HTML?", ["Un lenguaje de programación", "Lenguaje de marcado para páginas web"], 'b')
    },
    # ...otros conjuntos
]

def get_random_questions():
    return random.choice(conjuntos_preguntas)

def calculate_score(respuestas, preguntas):
    return sum(1 for k in preguntas if respuestas.get(k) == preguntas[k][2])