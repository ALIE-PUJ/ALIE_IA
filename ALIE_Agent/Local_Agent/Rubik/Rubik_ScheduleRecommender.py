import psycopg2
from psycopg2 import sql, Error
import os
import difflib

# DB Functions

# Create a new connection in each function
def create_connection():
    """
    Creates a new connection to the PostgreSQL database.
    """
    return psycopg2.connect(
        host=os.getenv('COCKROACHDB_HOST', 'localhost'),
        port=os.getenv('COCKROACHDB_PORT', 5432),
        user=os.getenv('COCKROACHDB_USER', 'root'),
        password=os.getenv('COCKROACHDB_PASS', 'pass'),
        database='alie_db'
    )

# GET Functions

# Función auxiliar para obtener todas las asignaturas y su semestre sugerido
def get_courses_and_semester_mapping():
    """
    Fetches all the courses and their suggested semester mapping.

    :return: A list of dictionaries with course ID, course name, semester, and course type.
    """
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = """
            SELECT 
                Curso.id_curso,
                Curso.nombre AS curso_nombre,
                Semestre_Sugerido.semestre,
                Semestre_Sugerido.tipo_curso
            FROM Curso
            JOIN Semestre_Sugerido ON Curso.id_curso = Semestre_Sugerido.id_curso
            ORDER BY Semestre_Sugerido.semestre ASC
            """
            cursor.execute(query)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Función auxiliar para obtener los cursos que ha visto un estudiante
def get_student_courses(student_id):
    """
    Fetches all the courses that a student has completed or enrolled in,
    including their grades.

    :param student_id: The ID of the student.
    :return: A list of dictionaries containing the course ID, course name, semester,
             course type, class ID, period, and grade.
    """
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = """
            SELECT 
                Curso.id_curso,
                Curso.nombre AS curso_nombre,
                Semestre_Sugerido.semestre,
                Semestre_Sugerido.tipo_curso,
                Clase.id_clase,      -- Include class ID
                Clase.periodo,       -- Include period
                Nota.nota            -- Include grade, it will be NULL if not found
            FROM Estudiante_Clase
            JOIN Clase ON Estudiante_Clase.id_clase = Clase.id_clase
            JOIN Curso ON Clase.id_curso = Curso.id_curso
            JOIN Semestre_Sugerido ON Curso.id_curso = Semestre_Sugerido.id_curso
            LEFT JOIN Nota ON Estudiante_Clase.id_clase = Nota.id_clase 
                            AND Estudiante_Clase.id_estudiante = Nota.id_estudiante
            WHERE Estudiante_Clase.id_estudiante = %s
            ORDER BY Semestre_Sugerido.semestre ASC
            """
            cursor.execute(query, (student_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Función auxiliar para obtener el mayor periodo de las clases
def get_max_period():
    """
    Fetches the maximum period from the Clase table to determine the next period.

    :return: The maximum period as a string or an error message.
    """
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = "SELECT MAX(periodo) FROM Clase"
            cursor.execute(query)
            result = cursor.fetchone()
            max_period = result[0]
            print("Max Period: ", max_period)
            return max_period
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Función auxiliar para obtener todos los periodos disponibles de las clases
def get_all_periods():
    """
    Fetches all distinct periods from the Clase table.

    :return: A list of distinct periods or an error message.
    """
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = "SELECT DISTINCT periodo FROM Clase ORDER BY periodo ASC"
            cursor.execute(query)
            result = cursor.fetchall()
            periods = [row[0] for row in result]
            print("Available Periods: ", periods)
            return periods
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()



# Mapping Functions

# Función auxiliar para obtener el pensum de los cursos
def get_course_mapping():
    """
    Fetches the course mapping and organizes it by semester.
    
    :return: A formatted string with the course mapping organized by semester.
    """
    # Obtener el mapeo de las asignaturas y sus semestres sugeridos
    course_mapping = get_courses_and_semester_mapping()
    
    if not isinstance(course_mapping, list):
        return f"Error fetching courses and semester mapping. {course_mapping}"

    # Agrupar los cursos por semestre
    semestres = {}
    for course in course_mapping:
        semestre = course['semestre']
        if semestre not in semestres:
            semestres[semestre] = []
        semestres[semestre].append(course)

    # Formatear el resultado de los cursos por semestre ascendente
    descripcion = "\n[PENSUM] Courses and their suggested semester mapping:\n"
    for semestre in sorted(semestres.keys()):  # Ordenar los semestres en orden ascendente
        descripcion += f"\nSemester {semestre}:\n"
        for course in semestres[semestre]:
            descripcion += (f"- Course ID: {course['id_curso']}, Name: {course['curso_nombre']} "
                            f"| Recommended semester: {course['semestre']}, Type: {course['tipo_curso']}\n")
    
    return descripcion


# Función auxiliar para obtener los cursos de un estudiante y su semestre actual
def get_student_info_mapping(student_id):
    """
    Fetches the courses taken by the student and determines their current semester.

    :param student_id: The ID of the student.
    :return: A formatted string with the student's courses, current semester, and grades.
    """
    student_courses = get_student_courses(student_id)

    if not isinstance(student_courses, list):
        return f"Error fetching student courses. {student_courses}"
    
    if not student_courses:
        return f"\n\n[STUDENT COURSES] No courses found for student ID {student_id}.\n"
    
    # Agrupar los cursos del estudiante por semestre
    semestres_estudiante = {}
    for course in student_courses:
        semestre = course['semestre']
        if semestre not in semestres_estudiante:
            semestres_estudiante[semestre] = []
        semestres_estudiante[semestre].append(course)

    # Formatear el resultado de los cursos del estudiante por semestre ascendente
    descripcion = f"\n\n[STUDENT COURSES] Courses taken by student ID {student_id}, ordered by suggested semester:\n"
    for semestre in sorted(semestres_estudiante.keys()):
        descripcion += f"\nSemester {semestre}:\n"
        for course in semestres_estudiante[semestre]:
            # Convert 'None' to 'N/A' for display
            grade = course['nota'] if course['nota'] is not None else 'N/A'
            descripcion += (f"- Course ID: {course['id_curso']}, Name: {course['curso_nombre']} "
                            f"(Class ID: {course['id_clase']}, Period: {course['periodo']}) | "
                            f"Grade: {grade} | "
                            f"Recommended semester: {course['semestre']}, Type: {course['tipo_curso']}\n")
    
    # Determinar el semestre actual basado en la cantidad de cursos por semestre
    semestre_actual = None
    for semestre, cursos in semestres_estudiante.items():
        if len(cursos) >= 3:  # Si ha tomado al menos 3 cursos en ese semestre
            if semestre_actual is None or semestre > semestre_actual:
                semestre_actual = semestre

    # Añadir el semestre actual al resultado
    if semestre_actual:
        descripcion += f"\n\n[CURRENT SEMESTER] The student is currently in semester {semestre_actual}.\n"
    else:
        descripcion += "\n\n[CURRENT SEMESTER] The student has not completed 3 courses in any semester yet.\n"

    return descripcion


# Función principal rubik
def rubik(student_id=None):
    """
    Main function to map all courses to their suggested semester and (optionally) show the courses a specific student has taken.
    
    :param student_id: The ID of the student (optional). If provided, fetches and displays the student's courses.
    :return: A formatted string with the course mapping and (if applicable) the student's courses and current semester.
    """

    # Obtener todos los periodos
    available_periods = get_all_periods()

    # Obtener el mayor periodo de las clases
    max_period = get_max_period()

    # Obtener el pensum de cursos
    descripcion = get_course_mapping()
    
    # Si se proporciona el student_id, obtener y mostrar los cursos del estudiante
    if student_id:
        descripcion += get_student_info_mapping(student_id)

    return descripcion


if __name__ == "__main__":
    student_id = 2
    print(rubik(student_id))  # Llamar a la función con un ID de estudiante
