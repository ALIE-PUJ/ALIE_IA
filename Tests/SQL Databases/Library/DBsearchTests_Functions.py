import psycopg2
from psycopg2 import sql, Error
import os

# Functions - Tools
from langchain.agents import tool

# Create a new connection in each function
def create_connection():
    """
    Creates a new connection to the PostgreSQL database.
    """
    return psycopg2.connect(
        host='localhost', 
        port=26257,
        user=os.getenv('USER', 'root'),
        password=os.getenv('PASS', ''),
        database='alie_db'
    )

# Funcion para buscar Estudiantes
def get_students_by_name_fetch(name: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT * FROM Estudiante WHERE LOWER(nombres) LIKE LOWER(%s)")
            cursor.execute(query, (f"%{name}%",))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Funciones para buscar Cursos por nombre
def get_course_by_name_fetch(course_name: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT * FROM Curso WHERE LOWER(nombre) LIKE LOWER(%s)")
            cursor.execute(query, (f"%{course_name}%",))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Funcion para buscar Clases por codigo de curso
def get_classes_by_course_code_fetch(course_code: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("""
                SELECT cl.id_clase, cl.periodo, cl.fecha_inicio, cl.fecha_final 
                FROM Clase cl
                WHERE cl.id_curso = %s
            """)
            cursor.execute(query, (course_code,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            
            if result_with_columns:
                # Mostrar la información del curso una sola vez
                curso_query = sql.SQL("SELECT nombre FROM Curso WHERE id_curso = %s")
                cursor.execute(curso_query, (course_code,))
                curso_result = cursor.fetchone()
                if curso_result:
                    curso_info = {'id_curso': course_code, 'nombre_curso': curso_result[0]}
                    result_with_columns.insert(0, curso_info)
            
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Funcion para buscar Clases por nombre de curso
def get_classes_by_course_name_fetch(course_name: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("""
                SELECT cu.id_curso, cu.nombre AS nombre_curso, cl.id_clase, cl.periodo, cl.fecha_inicio, cl.fecha_final 
                FROM Clase cl
                JOIN Curso cu ON cl.id_curso = cu.id_curso
                WHERE LOWER(cu.nombre) LIKE LOWER(%s)
            """)
            cursor.execute(query, (f"%{course_name}%",))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]

            if result_with_columns:
                # Mostrar la información del curso una sola vez
                curso_info = result_with_columns[0]
                for item in result_with_columns:
                    item['id_curso'] = curso_info['id_curso']
                    item['nombre_curso'] = curso_info['nombre_curso']
                result_with_columns = [result_with_columns[0]] + result_with_columns
            
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Funcion para buscar Clase por codigo
def get_class_by_code_fetch(course_code: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT * FROM Clase WHERE id_clase = %s")
            cursor.execute(query, (course_code,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Funcion para obtener Prerrequisitos de Cursos por nombre
def get_prerequisites_by_course_name_fetch(course_name: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("""
                SELECT c1.id_curso AS curso_id, c2.nombre AS curso_prerrequisito
                FROM Prerrequisito_Curso pc
                JOIN Curso c1 ON pc.id_curso = c1.id_curso
                JOIN Curso c2 ON pc.id_prerrequisito_curso = c2.id_curso
                WHERE LOWER(c1.nombre) LIKE LOWER(%s)
            """)
            cursor.execute(query, (f"%{course_name}%",))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]

            # Usar un set para evitar duplicaciones
            prerrequisitos_vistos = set()
            resultado_final = []
            if result_with_columns:
                curso_info = result_with_columns[0]
                for item in result_with_columns:
                    if item['curso_prerrequisito'] not in prerrequisitos_vistos:
                        prerrequisitos_vistos.add(item['curso_prerrequisito'])
                        item['curso_id'] = curso_info['curso_id']
                        resultado_final.append(item)
            
            return resultado_final
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Funcion para obtener Prerrequisitos de Cursos por ID
def get_prerequisites_by_course_code_fetch(course_code: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("""
                SELECT c1.id_curso AS curso_id, c2.nombre AS curso_prerrequisito
                FROM Prerrequisito_Curso pc
                JOIN Curso c1 ON pc.id_curso = c1.id_curso
                JOIN Curso c2 ON pc.id_prerrequisito_curso = c2.id_curso
                WHERE c1.id_curso = %s
            """)
            cursor.execute(query, (course_code,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]

            # Usar un set para evitar duplicaciones
            prerrequisitos_vistos = set()
            resultado_final = []
            if result_with_columns:
                curso_info = result_with_columns[0]
                for item in result_with_columns:
                    if item['curso_prerrequisito'] not in prerrequisitos_vistos:
                        prerrequisitos_vistos.add(item['curso_prerrequisito'])
                        item['curso_id'] = curso_info['curso_id']
                        resultado_final.append(item)
            
            return resultado_final
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()
        
# Función para obtener el horario de una clase
def get_class_schedule_fetch(class_id: str) -> list:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("""
                SELECT id_clase, dia, hora_inicio, hora_fin 
                FROM Horario_Clase
                WHERE id_clase = %s
            """)
            
            cursor.execute(query, (class_id,))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()

# Funcion para buscar Profesores
def get_teacher_by_name_fetch(teacher_name: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT * FROM Profesor WHERE LOWER(nombres) LIKE LOWER(%s)")
            cursor.execute(query, (f"%{teacher_name}%",))
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_with_columns = [dict(zip(columns, row)) for row in result]
            return result_with_columns
    except Error as e:
        return f"Error: {e}"
    finally:
        conn.close()





# Conversion a lenguaje natural

# Función para buscar estudiante por nombre y retornar en lenguaje natural
def get_students_by_name(name: str) -> str:
    """
    Searches for students by their name.
    The input is the student's name, and the function returns
    a list of students whose names match the input.
    
    :param nombre: The name of the student to search for.
    :return: A list of dictionaries representing students whose names match the input.
    
    Example call:
    get_students_by_name("Juan")
    """
    # Busca estudiantes por su nombre.
    # La entrada es el nombre del estudiante, y la función devuelve
    # una lista de estudiantes cuyos nombres coinciden con la entrada.
    resultados = get_students_by_name_fetch(name)  # Función original
    if not resultados:
        return f"There are no students with the name {name}."
    
    descripcion = f"I found {len(resultados)} students with the name '{name}':\n"
    for estudiante in resultados:
        descripcion += (
            f"- {estudiante['nombres']} {estudiante['apellidos']} (ID: {estudiante['id_estudiante']}), "
            f"born on {estudiante['fecha_nacimiento']}, "
            f"enrolled in the program with ID {estudiante['id_carrera']}, "
            f"email: {estudiante['email']}, "
            f"phone: {estudiante['telefono']}, "
            f"lives at {estudiante['direccion']}.\n"
        )
    return descripcion

# Función para buscar curso por nombre y retornar en lenguaje natural
def get_course_by_name(name: str) -> str:
    """
    Searches for courses by their name.
    The input is the course name, and the function returns
    a list of courses whose names match the input.
    
    :param nombre_curso: The name of the course to search for.
    :return: A list of dictionaries representing courses whose names match the input.
    
    Example call:
    get_course_by_name("Mathematics")
    """
    # Busca cursos por su nombre.
    # La entrada es el nombre del curso, y la función devuelve
    # una lista de cursos cuyos nombres coinciden con la entrada.
    resultados = get_course_by_name_fetch(name)  # Función original
    if not resultados:
        return f"There are no courses with the name {name}."

    descripcion = f"I found the following course: '{name}':\n"
    for curso in resultados:
        descripcion += (
            f"- Course: {curso['nombre']} (ID: {curso['id_curso']}), "
            f"Description: {curso['descripcion']}.\n"
        )
    return descripcion

# Función para buscar clases por código de curso y retornar en lenguaje natural
def get_classes_by_course_code(code: str) -> str:
    """
    Searches for classes by course code.
    The input is the course code, and the function returns
    a list of classes associated with that course code.
    
    :param codigo_curso: The code of the course to search for.
    :return: A list of dictionaries representing classes associated with the given course code.
    
    Example call:
    get_classes_by_course_code("1511")
    """
    # Busca clases por el código del curso.
    # La entrada es el código del curso, y la función devuelve
    # una lista de clases asociadas con ese código de curso.
    resultados = get_classes_by_course_code_fetch(code)  # Función original
    if not resultados or len(resultados) < 2:
        return f"There are no classes for the course with code '{code}'."

    # El primer elemento es la información del curso, así que lo omitimos
    descripcion = f"There are {len(resultados) - 1} classes for the course with code '{code}':\n"
    for clase in resultados[1:]:  # Empezamos desde el segundo elemento
        descripcion += (
            f"- Class ID: {clase['id_clase']}, "
            f"period: {clase['periodo']}, "
            f"from {clase['fecha_inicio']} to {clase['fecha_final']}.\n"
        )
    return descripcion

# Función para buscar clases por nombre de curso y retornar en lenguaje natural
def get_classes_by_course_name(name: str) -> str:
    """
    Searches for classes by course name.
    The input is the course name, and the function returns
    a list of classes associated with that course name.
    
    :param nombre_curso: The name of the course to search for.
    :return: A list of dictionaries representing classes associated with the given course name.
    
    Example call:
    get_classes_by_course_name("Mathematics")
    """
    # Busca clases por el nombre del curso.
    # La entrada es el nombre del curso, y la función devuelve
    # una lista de clases asociadas con ese nombre de curso.
    resultados = get_classes_by_course_name_fetch(name)  # Función original
    if not resultados:
        return f"There are no classes for the course '{name}'."

    descripcion = f"I found {len(resultados)} classes for the course '{name}':\n"
    for clase in resultados:
        descripcion += (
            f"- Class ID: {clase['id_clase']}, "
            f"period: {clase['periodo']}, "
            f"from {clase['fecha_inicio']} to {clase['fecha_final']}.\n"
        )
    return descripcion

# Función para buscar clase por código y retornar en lenguaje natural
def get_class_by_code(code: str) -> str:
    """
    Searches for a class by its code.
    The input is the class code, and the function returns
    details of the class with that code.
    
    :param codigo_clase: The code of the class to search for.
    :return: A list of dictionaries representing the class details.
    
    Example call:
    get_class_by_code("1511")
    """
    # Busca una clase por su código.
    # La entrada es el código de la clase, y la función devuelve
    # detalles de la clase con ese código.
    resultados = get_class_by_code_fetch(code)  # Función original
    if not resultados:
        return f"There are no classes with the code '{code}'."

    descripcion = f"I found a class with code '{code}':\n"
    for clase in resultados:
        descripcion += (
            f"- Class ID: {clase['id_clase']}, "
            f"corresponding to course ID: {clase['id_curso']}, "
            f"period: {clase['periodo']}, "
            f"from {clase['fecha_inicio']} to {clase['fecha_final']}.\n"
        )
    return descripcion

# Función para buscar prerrequisitos por nombre de curso y retornar en lenguaje natural
def get_prerequisites_by_course_name(name: str) -> str:
    """
    Searches for prerequisites of a course by course name.
    The input is the course name, and the function returns
    a list of prerequisites for that course.
    
    :param nombre_curso: The name of the course to search for prerequisites.
    :return: A list of dictionaries representing prerequisites for the course.
    
    Example call:
    get_prerequisites_by_course_name("Mathematics")
    """
    # Busca prerrequisitos de un curso por nombre del curso.
    # La entrada es el nombre del curso, y la función devuelve
    # una lista de prerrequisitos para ese curso.
    resultados = get_prerequisites_by_course_name_fetch(name)  # Función original
    if not resultados:
        return f"There are no prerequisites for the course '{name}'."

    descripcion = f"There are {len(resultados)} prerequisites for the course '{name}':\n"
    for prerrequisito in resultados:
        descripcion += f"- {prerrequisito['curso_prerrequisito']}.\n"
    return descripcion

# Función para buscar prerrequisitos por código de curso y retornar en lenguaje natural
def get_prerequisites_by_course_code(code: str) -> str:
    """
    Searches for prerequisites of a course by course code.
    The input is the course code, and the function returns
    a list of prerequisites for that course.
    
    :param codigo_curso: The code of the course for which prerequisites are to be searched.
    :return: A list of dictionaries representing prerequisites for the given course code.
    
    Example call:
    get_prerequisites_by_course_code("1511")
    """
    # Busca prerrequisitos de un curso por código del curso.
    # La entrada es el código del curso, y la función devuelve
    # una lista de prerrequisitos para ese curso.
    resultados = get_prerequisites_by_course_code_fetch(code)  # Función original
    if not resultados:
        return f"There are no prerequisites for the course with code '{code}'."

    descripcion = f"There are {len(resultados)} prerequisites for the course with code '{code}':\n"
    for prerrequisito in resultados:
        descripcion += f"- {prerrequisito['curso_prerrequisito']}.\n"
    return descripcion


# Función para obtener horarios de clases y retornar en lenguaje natural
def get_class_schedule(class_id: str) -> str:
    """
    Searches for the schedule(s) of a class by its class ID.
    The function returns the schedule(s) for the specified class.
    
    :param class_id: A single class ID to search for its schedule(s).
    :return: A description of the schedule(s) for the specified class.
    
    Example call:
    get_class_schedule("1511")
    """
    # Busca los horarios de una clase por su ID.
    resultado = get_class_schedule_fetch(class_id)
    if not resultado:
        return "I am sorry, no schedules were found for the specified class."

    descripcion = f"This are the schedules for class with ID {class_id}:\n"
    for horario in resultado:
        descripcion += (
            f"- Day: {horario['dia']}, "
            f"from {horario['hora_inicio']} to {horario['hora_fin']}.\n"
        )
    return descripcion

# Función para buscar profesor por nombre y retornar en lenguaje natural
def get_teacher_by_name(name: str) -> str:
    """
    Searches for professors by their name.
    The input is the professor's name, and the function returns
    a list of professors whose names match the input.
    
    :param nombre: The name of the professor to search for.
    :return: A description of professors whose names match the input.
    
    Example call:
    get_teacher_by_name("Carlos")
    """
    # Busca profesores por su nombre.
    # La entrada es el nombre del profesor, y la función devuelve
    # una lista de profesores cuyos nombres coinciden con la entrada.
    resultados = get_teacher_by_name_fetch(name)  # Función original
    if not resultados:
        return f"There are no professors with the name {name}."

    descripcion = f"There are {len(resultados)} professors with the name '{name}':\n"
    for profesor in resultados:
        descripcion += (
            f"- {profesor['nombres']} {profesor['apellidos']} (ID: {profesor['id_profesor']}), "
            f"Email: {profesor['email']}, "
            f"Phone: {profesor['telefono']}.\n"
        )
    return descripcion





# Función para escribir los resultados de las pruebas en un archivo
def escribirResultadosArchivo(nombreArchivo):
    # Abrir archivo para escritura
    with open(nombreArchivo, "w", encoding="utf-8") as file:

        # Pruebas

        # Buscar Estudiantes
        file.write("\nBuscando estudiante con nombre 'Juan':\n")
        file.write(str(get_students_by_name_fetch('Juan')) + "\n")

        # Buscar Cursos
        file.write("\nBuscando curso con nombre 'Estructuras de datos':\n")
        file.write(str(get_course_by_name_fetch('Estructuras de datos')) + "\n")

        # Buscar Clases
        file.write("\nBuscando clases del curso 'Estructuras de datos':\n")
        file.write(str(get_classes_by_course_name_fetch('Estructuras de datos')) + "\n")

        file.write("\nBuscando clases del curso con código '4196':\n")  # Estructuras de Datos tiene el código 4196
        file.write(str(get_classes_by_course_code_fetch(4196)) + "\n")

        file.write("\nBuscando clase con código '4590':\n")  # Ejemplo de clase de estructuras de datos
        file.write(str(get_class_by_code_fetch(4590)) + "\n")

        # Buscar Prerrequisitos
        file.write("\nBuscando prerrequisitos del curso 'Estructuras de datos':\n")
        file.write(str(get_prerequisites_by_course_name_fetch('Estructuras de datos')) + "\n")

        file.write("\nBuscando prerrequisitos del curso con código '4196':\n")  # Estructuras de Datos tiene el código 4196
        file.write(str(get_prerequisites_by_course_code_fetch(4196)) + "\n")

        # Obtener horarios de clases
        file.write("\nBuscando horarios para las clases con IDs: " + str("1557") + "\n")
        file.write(str(get_class_schedule_fetch("1557")) + "\n")

        # Obtener profesores
        file.write("\nBuscando profesores con nombre 'Carlos':\n")
        file.write(str(get_teacher_by_name_fetch("Carlos")) + "\n|")

        # Funciones auxiliares (Lenguaje natural)
        file.write("\n\n\nPruebas de conversión a Lenguaje Natural:\n")
        
        # Buscar Estudiantes
        file.write("\nBuscando estudiante con nombre 'Juan':\n")
        file.write(str(get_students_by_name('Juan')) + "\n")

        # Buscar Cursos
        file.write("\nBuscando curso con nombre 'Estructuras de datos':\n")
        file.write(str(get_course_by_name('Estructuras de datos')) + "\n")

        # Buscar Clases
        file.write("\nBuscando clases del curso 'Estructuras de datos':\n")
        file.write(str(get_classes_by_course_name('Estructuras de datos')) + "\n")

        file.write("\nBuscando clases del curso con código '4196':\n")  # Estructuras de Datos tiene el código 4196
        file.write(str(get_classes_by_course_code(4196)) + "\n")

        file.write("\nBuscando clase con código '4590':\n")  # Ejemplo de clase de estructuras de datos
        file.write(str(get_class_by_code(4590)) + "\n")

        # Buscar Prerrequisitos
        file.write("\nBuscando prerrequisitos del curso 'Estructuras de datos':\n")
        file.write(str(get_prerequisites_by_course_name('Estructuras de datos')) + "\n")

        file.write("\nBuscando prerrequisitos del curso con código '4196':\n")  # Estructuras de Datos tiene el código 4196
        file.write(str(get_prerequisites_by_course_code(4196)) + "\n")

        # Obtener horarios de clases
        file.write("\nBuscando horarios para las clases con IDs: " + str("1557") + "\n")
        file.write(str(get_class_schedule("1557")) + "\n")

        # Obtener profesores
        file.write("\nBuscando profesores con nombre 'Carlos':\n")
        file.write(str(get_teacher_by_name("Carlos")) + "\n")

        # Cerrar archivo
        file.close()


def main():

    # Escribir resultados en archivo
    escribirResultadosArchivo("resultados_pruebas_herramientas.txt")

if __name__ == '__main__':
    main()