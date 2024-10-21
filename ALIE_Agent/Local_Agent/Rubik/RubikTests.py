import psycopg2
import os

# Function to create connection to the database
def create_connection():
    return psycopg2.connect(
        host=os.getenv('COCKROACHDB_HOST', 'localhost'),
        port=os.getenv('COCKROACHDB_PORT', 5432),
        user=os.getenv('COCKROACHDB_USER', 'root'),
        password=os.getenv('COCKROACHDB_PASS', 'pass'),
        database='alie_db'
    )

# Function to get the most recent period
def get_max_period():
    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = "SELECT MAX(periodo) FROM Clase"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0]

# Function to get the completed courses by the student
def get_completed_courses(student_id):
    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT Curso.id_curso, Curso.nombre, Curso.creditos
            FROM Estudiante_Clase
            JOIN Clase ON Estudiante_Clase.id_clase = Clase.id_clase
            JOIN Curso ON Clase.id_curso = Curso.id_curso
            WHERE Estudiante_Clase.id_estudiante = %s
            """
            cursor.execute(query, (student_id,))
            return cursor.fetchall()

# Function to check prerequisites of courses
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

# Function to get recommended courses that the student has not taken
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
                cursor.execute(query)  # If no completed courses
            recommended_courses = cursor.fetchall()
            
            # Verify prerequisites
            recommended_courses_with_prereqs = []
            for course in recommended_courses:
                course_id = course[0]
                prereqs = check_prerequisites(course_id)
                prereqs_met = all(prereq in completed_course_ids for prereq in prereqs)
                recommended_courses_with_prereqs.append(
                    (course_id, course[1], course[2], prereqs_met, bool(prereqs))  # Add bool(prereqs) to know if there are prerequisites
                )

            return recommended_courses_with_prereqs

# Function to get classes and schedules for recommended courses in the latest period
def get_classes_in_latest_period_for_recommended_courses(recommended_courses):
    max_period = get_max_period()  # Get the maximum period
    
    # Extract course IDs from recommended courses
    course_ids = [course[0] for course in recommended_courses]

    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT Clase.id_clase, Clase.id_curso, Horario_Clase.dia, Horario_Clase.hora_inicio, Horario_Clase.hora_fin
            FROM Clase
            JOIN Horario_Clase ON Clase.id_clase = Horario_Clase.id_clase
            WHERE Clase.id_curso IN %s AND Clase.periodo = %s
            """
            if course_ids:
                cursor.execute(query, (tuple(course_ids), max_period))
                classes = cursor.fetchall()

                # Group classes by course ID
                classes_by_course = {}
                for cls in classes:
                    course_id = cls[1]
                    if course_id not in classes_by_course:
                        classes_by_course[course_id] = []
                    classes_by_course[course_id].append(cls)

                # Format and print the result
                print(f"\nClases disponibles en el periodo {max_period} para los cursos recomendados:\n")
                for course_id, class_list in classes_by_course.items():
                    # Get the course name from recommended courses
                    course_name = next(course[1] for course in recommended_courses if course[0] == course_id)
                    print(f"Curso: {course_name} (ID: {course_id})")
                    for cls in class_list:
                        print(f"  - Clase ID: {cls[0]}, Día: {cls[2]}, Hora Inicio: {cls[3]}, Hora Fin: {cls[4]} (Periodo: {max_period})")
            else:
                print("No hay cursos recomendados disponibles en el periodo más reciente.")

# Function to print recommended courses
def print_recommended_courses(recommended_courses):
    print("Cursos recomendados para el estudiante:")
    for course in recommended_courses:
        # Check if the course has prerequisites
        if course[4]:  # If it has prerequisites
            prereq_status = "(Prerequisito cumplido)" if course[3] else "(Prerequisito no cumplido)"
        else:
            prereq_status = "(Sin prerrequisitos)"
        
        print(f"- ID: {course[0]}, Nombre: {course[1]}, Créditos: {course[2]} {prereq_status}")

# Example usage
if __name__ == "__main__":
    student_id = 2  # Student ID
    recommended_courses = get_recommended_courses(student_id)
    print_recommended_courses(recommended_courses)

    # Get and print classes in the latest period for recommended courses
    get_classes_in_latest_period_for_recommended_courses(recommended_courses)
