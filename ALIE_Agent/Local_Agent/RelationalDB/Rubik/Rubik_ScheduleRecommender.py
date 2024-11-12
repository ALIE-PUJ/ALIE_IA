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
    # print("Cursos completados por el estudiante:", completed_courses)
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

            # Filter out courses where prerequisites are not met
            recommended_courses_with_prereqs = [
                course for course in recommended_courses_with_prereqs if course[3] or not course[4]
            ]

            return recommended_courses_with_prereqs

# Function to get classes and schedules for recommended courses in the latest period
def get_classes_in_latest_period_for_recommended_courses(recommended_courses):
    max_period = get_max_period()  # Get the maximum period
    # max_period = "2024-3"

    # print("Target period:", max_period)

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
    print("\nCursos recomendados para el estudiante:")
    for course in recommended_courses:
        # Check if the course has prerequisites
        if course[4]:  # If it has prerequisites
            prereq_status = "(Prerequisito cumplido)" if course[3] else "(Prerequisito no cumplido)"
        else:
            prereq_status = "(Sin prerrequisitos)"
        
        print(f"- ID: {course[0]}, Nombre: {course[1]}, Créditos: {course[2]} {prereq_status}")

# Function to return recommended courses as a string
def get_recommended_courses_text(recommended_courses):
    result = "\nCursos recomendados para el estudiante:\n"
    for course in recommended_courses:
        # Check if the course has prerequisites
        if course[4]:  # If it has prerequisites
            prereq_status = "(Prerequisito cumplido)" if course[3] else "(Prerequisito no cumplido)"
        else:
            prereq_status = "(Sin prerrequisitos)"
        
        result += f"- ID: {course[0]}, Nombre: {course[1]}, Créditos: {course[2]} {prereq_status}\n"
    
    return result

# Function to print classes
def print_classes(classes_by_course, max_period, recommended_courses):
    if not classes_by_course:
        print("No hay clases disponibles en el periodo más reciente para los cursos recomendados.")
        return

    print(f"Clases disponibles en el periodo {max_period} para los cursos recomendados:\n")
    for course_id, class_list in classes_by_course.items():
        # Get the course name from recommended courses
        course_name = next(course[1] for course in recommended_courses if course[0] == course_id)
        print(f"Curso: {course_name} (ID: {course_id})")
        for cls in class_list:
            print(f"  - Clase ID: {cls[0]}, Día: {cls[2]}, Hora Inicio: {cls[3]}, Hora Fin: {cls[4]} (Periodo: {max_period})")
    print("\n")

# Function to return classes as a string
def get_classes_text(classes_by_course, max_period, recommended_courses):
    if not classes_by_course:
        return "No hay clases disponibles en el periodo más reciente para los cursos recomendados."

    result = f"Clases disponibles en el periodo {max_period} para los cursos recomendados:\n\n"
    
    for course_id, class_list in classes_by_course.items():
        # Get the course name from recommended courses
        course_name = next(course[1] for course in recommended_courses if course[0] == course_id)
        result += f"Curso: {course_name} (ID: {course_id})\n"
        for cls in class_list:
            result += f"  - Clase ID: {cls[0]}, Día: {cls[2]}, Hora Inicio: {cls[3]}, Hora Fin: {cls[4]} (Periodo: {max_period})\n"
    
    return result + "\n"

# Function to create schedules
def create_schedules(classes_by_course, recommended_courses):

    def check_other_conflicts(schedule, classes_by_course, selected_cls):
        class_id = selected_cls[0]
        selected_course_id = selected_cls[1]
        #print(f"Checking conflicts for class: {class_id}")

        alternative_classes = [session for session in classes_by_course.get(selected_course_id, []) if session[0] == class_id]

        if alternative_classes:
            #print(f"Alternative sessions found for class {class_id}: {alternative_classes}")
            ex1 = 0
        else:
            #print(f"No alternative sessions found for class {class_id}")
            ex2 = 0

        # Initialize a list to store non-conflicting classes
        non_conflicting_classes = []

        for alt_cls in alternative_classes:
            if is_conflict(schedule, alt_cls):
                #print(f"Conflict found when trying to add alternative class {alt_cls[0]} with schedule {alt_cls}")
                return False, None
            else:
                # If there's no conflict, add the class to the non-conflicting list
                non_conflicting_classes.append(alt_cls)

        return True, non_conflicting_classes

    def is_conflict(schedule, new_class):
        if new_class is None:  # No conflict for classes without schedule
            return False
        new_day, new_start, new_end = new_class[2], new_class[3], new_class[4]
        for _, classes in schedule:
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
        schedule_onlyIds = []
        total_credits = 0
        courses_added = set()

        all_classes = []
        for course in recommended_courses:
            course_id = course[0]
            if course_id in classes_by_course:
                all_classes.extend([(course_id, cls) for cls in classes_by_course[course_id]])
            else:
                all_classes.append((course_id, None))  # Classes without schedule

        sorted_classes = sorted(
            [c for c in all_classes if c[1] is not None],
            key=lambda x: x[1][3] if x[1] is not None else time(23, 59)  # Sort by start time
        ) + [c for c in all_classes if c[1] is None]

        if not prefer_day:
            sorted_classes.reverse()

        for course_id, cls in sorted_classes:
            if course_id in courses_added:
                continue

            if cls is None:
                # print(f"Adding class without schedule: Course ID {course_id}")
                schedule.append((course_id, [None]))
                courses_added.add(course_id)
                total_credits += sum(c[2] for c in recommended_courses if c[0] == course_id)

                if total_credits >= max_credits:
                    break

            if cls is not None:
                start_time = datetime.combine(datetime.today(), cls[3]).time()
                
                # If diurnal schedule only add classes that end before 18:00
                # If nocturnal schedule only add classes that start after 14:00
                if (prefer_day and start_time >= time(18, 0)) or (not prefer_day and start_time < time(14, 0)):
                    continue

                has_no_conflict, non_conflicting_classes = check_other_conflicts(schedule, classes_by_course, (cls[0], course_id))
                if not is_conflict(schedule, cls) and has_no_conflict:
                    #print(f"Adding class to schedule: {cls[0]}. No conflicts found.")
                    schedule.append((course_id, [cls]))

                    for alt_cls in non_conflicting_classes:
                        #  (Only if its not the base class session)
                        if alt_cls != cls:
                            schedule[-1][1].append(alt_cls)

                    schedule_onlyIds.append(cls[0])
                    courses_added.add(course_id)
                    total_credits += sum(c[2] for c in recommended_courses if c[0] == course_id)

                    # Esto permite tener un margen de tolerancia de 1-2-3 créditos, por lo general
                    if total_credits >= max_credits:
                        break
        #else:
            #return None  # No schedule found

        return schedule, schedule_onlyIds

    schedules = []
    schedules_onlyIds = []
    for load, credits in [("baja", 10), ("media", 18), ("alta", 25)]:
        day_schedule, day_schedule_onlyIds = generate_schedule(credits, prefer_day=True)
        night_schedule, night_schedule_onlyIds = generate_schedule(credits, prefer_day=False)
        if day_schedule is not None:
            schedules.append(day_schedule)
            schedules_onlyIds.append(f"{load} diurna: {day_schedule_onlyIds}")
        if night_schedule is not None:
            schedules.append(night_schedule)
            schedules_onlyIds.append(f"{load} nocturna: {night_schedule_onlyIds}")

    return schedules, schedules_onlyIds

# Function to print schedules
def print_schedules(schedules, classes_by_course, recommended_courses):
    load_names = ["Baja (Alrededor de 10 créditos)", "Media (Alrededor de 18 créditos)", "Alta (Alrededor de 25 créditos)"]

    max_period = get_max_period()
    print(f"**Horarios generados para el siguiente periodo de inscripcion ({max_period})**:")

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

                print(f"Curso: {course_info[1]} (ID: {course_id}) [{course_info[2]} créditos]")

                for cls in classes:
                    if cls is not None:
                        print(f"  Clase ID: {cls[0]}, Día: {cls[2]}, Hora Inicio: {cls[3]}, Hora Fin: {cls[4]}")
                    else:
                        print("  Horario no especificado")

                total_credits += course_info[2]

            print(f"Total de créditos: {total_credits}")
            print()  # Add an empty line between Diurno and Nocturno schedules

# Function to return schedules as a string
def get_schedules_text(schedules, classes_by_course, recommended_courses):
    load_names = ["Baja (Alrededor de 10 créditos)", "Media (Alrededor de 18 créditos)", "Alta (Alrededor de 25 créditos)"]
    
    max_period = get_max_period()  # Assuming this function is defined elsewhere
    result = f"**Horarios generados para el siguiente periodo de inscripción ({max_period})**:\n"

    for i in range(0, len(schedules), 2):
        result += f"\n**Horarios para carga {load_names[i//2]}**\n"

        for j, period in enumerate(["Diurno", "Nocturno"]):
            result += f"{period}\n"
            schedule = schedules[i+j]
            total_credits = 0

            for course_id, classes in schedule:
                course_info = next((c for c in recommended_courses if c[0] == course_id), None)
                if course_info is None:
                    result += f"Advertencia: No se encontró información para el curso ID: {course_id}\n"
                    continue

                result += f"Curso: {course_info[1]} (ID: {course_id}) [{course_info[2]} créditos]\n"

                for cls in classes:
                    if cls is not None:
                        result += f"  Clase ID: {cls[0]}, Día: {cls[2]}, Hora Inicio: {cls[3]}, Hora Fin: {cls[4]}\n"
                    else:
                        result += "  Horario no especificado\n"

                total_credits += course_info[2]

            result += f"Total de créditos: {total_credits}\n"
            result += "\n"  # Add an empty line between Diurno and Nocturno schedules
    
    return result

# Function to generate schedules for a student
def rubik_schedule_generator(student_id=None):

    try:
        # print("Generando horarios para el estudiante con ID:", student_id)
        student_text = f"Generando horarios para el estudiante con ID: {student_id}"

        recommended_courses = get_recommended_courses(student_id)
        
        if recommended_courses:
            # Recommended courses
            # print_recommended_courses(recommended_courses)
            recommended_courses_text = get_recommended_courses_text(recommended_courses)
            # print(recommended_courses_text)

            # Classes in the latest period for recommended courses
            classes_by_course, max_period = get_classes_in_latest_period_for_recommended_courses(recommended_courses)
            # print("classes_by_course:", classes_by_course)
            classes_text = get_classes_text(classes_by_course, max_period, recommended_courses)
            # print_classes(classes_by_course, max_period, recommended_courses)

            # Schedules
            schedules, schedules_onlyIds = create_schedules(classes_by_course, recommended_courses)
            # print_schedules(schedules, classes_by_course, recommended_courses)
            schedules_text = get_schedules_text(schedules, classes_by_course, recommended_courses)
            # print(schedules_text)
            # print("Schedules only IDs:", schedules_onlyIds)

            return student_text + "\n" + recommended_courses_text +  "\n" + classes_text + "\n" + schedules_text
        else:
            # print("No hay cursos recomendados para el estudiante.")
            return "No hay cursos recomendados para el estudiante. Probablemente ya ha completado todos los cursos."
    except Exception as e:
        error_message = f"Ocurrió un error al generar los horarios. Intente más tarde."
        # print(error_message)
        return error_message

# Example usage
if __name__ == "__main__":
    student_id = 3
    rubik_text = rubik_schedule_generator(student_id)
    print(rubik_text)

    # Una clase diurna acaba como maximo a las 18:00, y una clase nocturna empieza como minimo a las 14:00