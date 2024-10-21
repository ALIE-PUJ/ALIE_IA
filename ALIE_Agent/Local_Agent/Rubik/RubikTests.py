import psycopg2
import os
from itertools import combinations
from collections import defaultdict
from datetime import time

# Función para crear conexión a la base de datos
def create_connection():
    return psycopg2.connect(
        host=os.getenv('COCKROACHDB_HOST', 'localhost'),
        port=os.getenv('COCKROACHDB_PORT', 5432),
        user=os.getenv('COCKROACHDB_USER', 'root'),
        password=os.getenv('COCKROACHDB_PASS', 'pass'),
        database='alie_db'
    )

# Función para obtener los cursos completados por el estudiante
def get_completed_courses(student_id):
    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT Curso.id_curso, Curso.nombre, Curso.creditos
            FROM Nota
            JOIN Curso ON Nota.id_curso = Curso.id_curso
            WHERE Nota.id_estudiante = %s
            """
            cursor.execute(query, (student_id,))
            return cursor.fetchall()

# Función para verificar los prerrequisitos de los cursos
def check_prerequisites(course_id):
    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT id_prerrequisito_curso
            FROM Prerrequisito_Curso
            WHERE id_curso = %s
            """
            cursor.execute(query, (course_id,))
            return [row[0] for row in cursor.fetchall()]

# Función para obtener los cursos recomendados que el estudiante no ha tomado
def get_recommended_courses(student_id):
    completed_courses = get_completed_courses(student_id)
    completed_course_ids = [course[0] for course in completed_courses]

    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT Curso.id_curso, Curso.nombre, Curso.creditos
            FROM Curso
            WHERE Curso.id_curso NOT IN %s
            """
            if completed_course_ids:
                cursor.execute(query, (tuple(completed_course_ids),))
            else:
                cursor.execute(query)  # Si no hay cursos completados
            recommended_courses = cursor.fetchall()
            
            # Verificar prerrequisitos
            recommended_courses_with_prereqs = []
            for course in recommended_courses:
                course_id = course[0]
                prereqs = check_prerequisites(course_id)
                prereqs_met = all(prereq in completed_course_ids for prereq in prereqs)
                recommended_courses_with_prereqs.append(
                    (course_id, course[1], course[2], prereqs_met, bool(prereqs))  # Agregar bool(prereqs) para saber si tiene prer requisitos
                )

            return recommended_courses_with_prereqs

# Función para obtener las clases y sus horarios
def get_classes_and_schedule(course_ids):
    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT Clase.id_clase, Clase.id_curso, Horario_Clase.dia, Horario_Clase.hora_inicio, Horario_Clase.hora_fin
            FROM Clase
            JOIN Horario_Clase ON Clase.id_clase = Horario_Clase.id_clase
            WHERE Clase.id_curso IN %s
            """
            cursor.execute(query, (tuple(course_ids),))
            return cursor.fetchall()

# Función para obtener los horarios de las clases
def print_recommended_courses(recommended_courses):
    print("Cursos recomendados para el estudiante:")
    for course in recommended_courses:
        # Verifica si el curso tiene prerrequisitos
        if course[4]:  # Si tiene prerrequisitos
            prereq_status = "(Prerequisito cumplido)" if course[3] else "(Prerequisito no cumplido)"
        else:
            prereq_status = "(Sin prerrequisitos)"
        
        print(f"- ID: {course[0]}, Nombre: {course[1]}, Créditos: {course[2]} {prereq_status}")

# Ejemplo de uso
if __name__ == "__main__":
    student_id = 2  # ID del estudiante
    recommended_courses = get_recommended_courses(student_id)
    print_recommended_courses(recommended_courses)

