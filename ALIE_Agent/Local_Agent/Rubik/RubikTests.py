import psycopg2
import os
import random
from datetime import datetime, time

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
# 15 course limit. Organized by semester (ascending) to prioritize lower semester courses
def get_recommended_courses(student_id):
    completed_courses = get_completed_courses(student_id)
    print("Cursos completados por el estudiante:", completed_courses)
    completed_course_ids = [course[0] for course in completed_courses]

    with create_connection() as conn:
        with conn.cursor() as cursor:
            query = """
            SELECT Curso.id_curso, Curso.nombre, Curso.creditos, Semestre_Sugerido.semestre
            FROM Curso
            JOIN Semestre_Sugerido ON Curso.id_curso = Semestre_Sugerido.id_curso
            WHERE Curso.id_curso NOT IN %s
            ORDER BY Semestre_Sugerido.semestre ASC
            LIMIT 15  -- Limitar a un máximo de 15 cursos recomendados
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
                    (course_id, course[1], course[2], prereqs_met, bool(prereqs), course[3])  # Add recommended semester
                )

            return recommended_courses_with_prereqs

# Function to get classes and schedules for recommended courses in the latest period
def get_classes_in_latest_period_for_recommended_courses(recommended_courses):
    max_period = get_max_period()  # Get the maximum period
    max_period = "2024-3"

    print("Target period:", max_period)

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

                return classes_by_course, max_period
            else:
                return {}, max_period  # Return empty dict if no recommended courses

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

# Function to print classes
def print_classes(classes_by_course, max_period):
    if not classes_by_course:
        print("No hay clases disponibles en el periodo más reciente para los cursos recomendados.")
        return

    print(f"\nClases disponibles en el periodo {max_period} para los cursos recomendados:\n")
    for course_id, class_list in classes_by_course.items():
        # Get the course name from recommended courses
        course_name = next(course[1] for course in recommended_courses if course[0] == course_id)
        print(f"Curso: {course_name} (ID: {course_id})")
        for cls in class_list:
            print(f"  - Clase ID: {cls[0]}, Día: {cls[2]}, Hora Inicio: {cls[3]}, Hora Fin: {cls[4]} (Periodo: {max_period})")

def create_schedules(classes_by_course, recommended_courses):

    def check_other_conflicts(schedule, classes_by_course, selected_cls, sorted_classes):
        # Obtenemos el id de la clase actual
        class_id = selected_cls[0]
        selected_course_id = selected_cls[1]
        print("Checking conflicts for class:", class_id)

        # Obtener todas las sesiones de la misma clase (mismo id_clase)
        alternative_classes = [session for session in classes_by_course.get(selected_course_id, []) if session[0] == class_id]

        if alternative_classes:
            # print("All the sessions found for the selected class:", alternative_classes)
            found_alternative_classes = True
        else:
            print("No sessions found for the selected class")

        # print("sorted_classes: ", sorted_classes)

        alternative_class_conflict = True # Assume there is a conflict

        # Return the alternative class sessions conflict
        for course_id, cls in sorted_classes:
            # print("Checking course:", course_id)

            if cls is not None and course_id == selected_course_id:
                # print("Checking class:", cls[0], "against class:", class_id)
                if cls[0] == class_id:
                    print("Found the same class, with class id ", cls[0])
                    # Check if there is a conflict
                    alternative_class_conflict = is_conflict(schedule, cls)
                    print("Checking for specific Alternative class conflict with class", cls[0], ". Specific schedule: ", cls, ". Result: ", alternative_class_conflict)

                    # If there is a conflict, return False
                    if alternative_class_conflict:
                        print("Conflict found. Returning False")
                        return False

        # Return the alternative class sessions conflict, but negate it to return the opposite
        print("Returning not alternative_class_conflict: ", not alternative_class_conflict)
        return not alternative_class_conflict

        return False

    def is_conflict(schedule, new_class):
        if new_class is None:  # No conflict for classes without schedule
            return False
        new_day, new_start, new_end = new_class[2], new_class[3], new_class[4]
        for _, classes in schedule:  # Check against all classes in the schedule
            for cls in classes:
                if cls is None:
                    continue
                if cls[2] == new_day and (
                    (new_start <= cls[3] < new_end) or
                    (new_start < cls[4] <= new_end) or
                    (cls[3] <= new_start and new_end <= cls[4])
                ):
                    return True
        return False

    def generate_schedule(max_credits, prefer_day):
        schedule = []
        total_credits = 0
        courses_added = set()

        # Combine classes with schedule and without schedule
        all_classes = []
        for course in recommended_courses:
            course_id = course[0]
            if course_id in classes_by_course:
                all_classes.extend([(course_id, cls) for cls in classes_by_course[course_id]])
            else:
                all_classes.append((course_id, None))  # Classes without schedule

        # Sort classes with schedule, put classes without schedule at the end
        sorted_classes = sorted(
            [c for c in all_classes if c[1] is not None],
            key=lambda x: x[1][3] if x[1] is not None else time(23, 59)  # Sort by start time
        ) + [c for c in all_classes if c[1] is None]

        if not prefer_day:
            sorted_classes.reverse()  # For night preference, reverse the order

        for course_id, cls in sorted_classes:
            if course_id in courses_added:
                continue

            if cls is not None:
                start_time = datetime.combine(datetime.today(), cls[3]).time()
                if (prefer_day and start_time >= time(18, 0)) or (not prefer_day and start_time < time(18, 0)):
                    continue

                if not is_conflict(schedule, cls) and check_other_conflicts(schedule, classes_by_course, cls, sorted_classes) == True:
                    print("Adding class to schedule: #", cls[0], ". No conflicts found.")

                    schedule.append((course_id, [cls]))
                    courses_added.add(course_id)
                    total_credits += sum(c[2] for c in recommended_courses if c[0] == course_id)

                    if total_credits >= max_credits:
                        break
        else:
            return []  # No schedule found

        return schedule

    schedules = []
    for load, credits in [("baja", 10), ("media", 18), ("alta", 25)]:
        day_schedule = generate_schedule(credits, prefer_day=True)
        night_schedule = generate_schedule(credits, prefer_day=False)
        schedules.extend([day_schedule, night_schedule])

    return schedules

def print_schedules(schedules, classes_by_course, recommended_courses):
    load_names = ["Baja (hasta 10 créditos)", "Media (Hasta 18 créditos)", "Alta (Hasta 25 créditos)"]

    for i in range(0, len(schedules), 2):
        print(f"\nHorarios para carga {load_names[i//2]}")

        for j, period in enumerate(["Diurno", "Nocturno"]):
            print(f"{period}")
            schedule = schedules[i+j]
            total_credits = 0

            for course_id, classes in schedule:
                course_info = next((c for c in recommended_courses if c[0] == course_id), None)
                if course_info is None:
                    print(f"Advertencia: No se encontró información para el curso ID: {course_id}")
                    continue

                print(f"Curso: {course_info[1]} (ID: {course_id})")

                for cls in classes:
                    if cls is not None:
                        print(f"  Clase ID: {cls[0]}, Día: {cls[2]}, Hora Inicio: {cls[3]}, Hora Fin: {cls[4]}")
                    else:
                        print("  Horario no especificado")

                total_credits += course_info[2]

            print(f"Total de créditos: {total_credits}")
            print()  # Add an empty line between Diurno and Nocturno schedules

# Example usage
if __name__ == "__main__":
    student_id = 2
    recommended_courses = get_recommended_courses(student_id)
    if recommended_courses:
        print_recommended_courses(recommended_courses)
        # Get classes in the latest period for recommended courses
        classes_by_course, max_period = get_classes_in_latest_period_for_recommended_courses(recommended_courses)
        print("classes_by_course:", classes_by_course)
        print_classes(classes_by_course, max_period)

        # Create schedules
        print("\nHorarios...")
        schedules = create_schedules(classes_by_course, recommended_courses)
        print_schedules(schedules, classes_by_course, recommended_courses)
    else:
        print("No hay cursos recomendados para el estudiante.")