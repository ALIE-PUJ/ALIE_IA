import psycopg2
from psycopg2 import sql, Error
import os
import difflib

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


# Course filtering
def find_course_name(course_name: str) -> str:
    """
    Procesa la consulta para extraer el nombre del curso al que hace referencia.
    Maneja variaciones ortográficas y consultas en inglés o con errores.
    """
    # Diccionario de cursos con posibles variaciones en español e inglés
    cursos_dict = {
        'calculo diferencial': 'Calculo Diferencial',
        'differential calculus': 'Calculo Diferencial',
        'logica y matematicas discretas': 'Logica y Matematicas Discretas',
        'logic and discrete mathematics': 'Logica y Matematicas Discretas',
        'introduccion a la programacion': 'Introduccion a la Programación',
        'introduction to programming': 'Introduccion a la Programación',
        'pensamiento sistemico': 'Pensamiento Sistemico',
        'systems thinking': 'Pensamiento Sistemico',
        'introduccion a la ingenieria': 'Introduccion a la Ingenieria',
        'introduction to engineering': 'Introduccion a la Ingenieria',
        'constitucion y derecho civil': 'Constitución y Derecho Civil',
        'constitution and civil law': 'Constitución y Derecho Civil',
        'calculo integral': 'Calculo Integral',
        'integral calculus': 'Calculo Integral',
        'fisica mecanica': 'Fisica Mecánica',
        'mechanical physics': 'Fisica Mecánica',
        'algebra lineal': 'Algebra Lineal',
        'linear algebra': 'Algebra Lineal',
        'programacion avanzada': 'Programación Avanzada',
        'advanced programming': 'Programación Avanzada',
        'ecuaciones diferenciales': 'Ecuaciones Diferenciales',
        'differential equations': 'Ecuaciones Diferenciales',
        'proyecto de diseño en ingenieria': 'Proyecto de Diseño en Ingenieria',
        'engineering design project': 'Proyecto de Diseño en Ingenieria',
        'significacion teologica': 'Significación Teologica',
        'theological significance': 'Significación Teologica',
        'calculo vectorial': 'Calculo Vectorial',
        'vector calculus': 'Calculo Vectorial',
        'probabilidad y estadistica': 'Probabilidad y Estadistica',
        'probability and statistics': 'Probabilidad y Estadistica',
        'analisis y diseño de software': 'Analisis y Diseño de Software',
        'software analysis and design': 'Analisis y Diseño de Software',
        'bases de datos': 'Bases de Datos',
        'databases': 'Bases de Datos',
        'arquitectura y organizacion del computador': 'Arquitectura y Organizacion del Computador',
        'computer architecture and organization': 'Arquitectura y Organizacion del Computador',
        'proyecto social universitario': 'Proyecto Social Universitario',
        'university social project': 'Proyecto Social Universitario',
        'estructuras de datos': 'Estructuras de Datos',
        'data structures': 'Estructuras de Datos',
        'analisis numerico': 'Analisis Numerico',
        'numerical analysis': 'Analisis Numerico',
        'fundamentos de ingenieria de software': 'Fundamentos de Ingenieria de Software',
        'software engineering fundamentals': 'Fundamentos de Ingenieria de Software',
        'sistemas operativos': 'Sistemas Operativos',
        'operating systems': 'Sistemas Operativos',
        'desarrollo web': 'Desarrollo Web',
        'web development': 'Desarrollo Web',
        'fundamentos de seguridad de la informacion': 'Fundamentos de Seguridad de la Informacion',
        'information security fundamentals': 'Fundamentos de Seguridad de la Informacion',
        'teoria de la computacion': 'Teoria de la Computacion',
        'theory of computation': 'Teoria de la Computacion',
        'sistemas de informacion': 'Sistemas de Informacion',
        'information systems': 'Sistemas de Informacion',
        'inteligencia artificial': 'Inteligencia Artificial',
        'artificial intelligence': 'Inteligencia Artificial',
        'gestion de proyectos de innovacion y emprendimiento de ti': 'Gestion de Proyectos de Innovacion y Emprendimiento de TI',
        'it innovation and entrepreneurship project management': 'Gestion de Proyectos de Innovacion y Emprendimiento de TI',
        'arquitectura de software': 'Arquitectura de Software',
        'software architecture': 'Arquitectura de Software',
        'tecnologias digitales emergentes': 'Tecnologias Digitales Emergentes',
        'emerging digital technologies': 'Tecnologias Digitales Emergentes',
        'gestion financiera de proyectos de ti': 'Gestion Financiera de Proyectos de TI',
        'financial management of it projects': 'Gestion Financiera de Proyectos de TI',
        'gerencia estrategica de ti': 'Gerencia Estrategica de TI',
        'strategic it management': 'Gerencia Estrategica de TI',
        'optimizacion y simulacion': 'Optimizacion y Simulacion',
        'optimization and simulation': 'Optimizacion y Simulacion',
        'planeacion de proyecto final': 'Planeacion de Proyecto Final',
        'final project planning': 'Planeacion de Proyecto Final',
        'proyecto de innovacion y emprendimiento': 'Proyecto de Innovacion y Emprendimiento',
        'innovation and entrepreneurship project': 'Proyecto de Innovacion y Emprendimiento',
        'comunicaciones y redes': 'Comunicaciones y Redes',
        'communications and networks': 'Comunicaciones y Redes',
        'introduccion a sistemas distribuidos': 'Introduccion a Sistemas Distribuidos',
        'introduction to distributed systems': 'Introduccion a Sistemas Distribuidos',
        'proyecto de grado': 'Proyecto de Grado',
        'thesis project': 'Proyecto de Grado',
        'etica en la era de la informacion': 'Etica en la Era de la Informacion',
        'ethics in the information age': 'Etica en la Era de la Informacion',
        'epistemologia de la ingenieria': 'Epistemologia de la Ingenieria',
        'epistemology of engineering': 'Epistemologia de la Ingenieria',
        'introduccion a la computacion movil': 'Introduccion a la Computacion Movil',
        'introduction to mobile computing': 'Introduccion a la Computacion Movil',
        'fe y compromiso del ingeniero': 'Fe y Compromiso del Ingeniero',
        'faith and commitment of the engineer': 'Fe y Compromiso del Ingeniero',
        'analisis de algoritmos': 'Analisis de algoritmos',
        'algorithm analysis': 'Analisis de algoritmos',
    }

    # Limpiar la consulta
    course_name = course_name.lower()

    # Buscar el curso más cercano en el diccionario
    curso_match = difflib.get_close_matches(course_name, cursos_dict.keys(), n=1, cutoff=0.5) # Ajusar cutoff si es necesario
    
    # Devolver el nombre oficial del curso si se encuentra una coincidencia
    if curso_match:
        print(f"[DB COURSES] Course name matched: {curso_match[0]} with {cursos_dict[curso_match[0]]}")
        return cursos_dict[curso_match[0]] # Devolver el curso más cercano
    else:
        print(f"[DB COURSES] No course name matched. Returning base one: {course_name}")
        return course_name # Si no se encuentra una coincidencia, devolver el curso original


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

# Funcion para buscar Curso por codigo
def get_course_by_code_fetch(course_code: str) -> str:
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT * FROM Curso WHERE id_curso = %s")
            cursor.execute(query, (course_code,))
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
# Redireccion: NO
def get_students_by_name(argument: str) -> str:
    """
    Searches for students by their name.
    The input is the student's name, and the function returns
    a list of students whose names match the input.
    
    :param argument: The name of the student to search for.
    :return: A list of dictionaries representing students whose names match the input.
    
    Example call:
    get_students_by_name("Juan")
    """
    # Busca estudiantes por su nombre.
    # La entrada es el nombre del estudiante, y la función devuelve
    # una lista de estudiantes cuyos nombres coinciden con la entrada.
    resultados = get_students_by_name_fetch(argument)  # Función original
    if not resultados:
        return f"There are no students with the name {argument}."
    
    descripcion = f"I found {len(resultados)} students with the name '{argument}':\n"
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
# Redireccion: SI. a get_course_by_code
def get_course_by_name(argument: str) -> str:
    """
    Searches for courses by their name.
    The input is the course name, and the function returns
    a list of courses whose names match the input.
    
    :param argument: The name of the course to search for.
    :return: A list of dictionaries representing courses whose names match the input.
    
    Example call:
    get_course_by_name("Mathematics")
    """

    # Si el argumento es un número, redirigir a get_course_by_code
    if argument.isdigit():
        print("[DBSearch] received a number, redirecting to get_course_by_code")
        return get_course_by_code(argument)

    # Busca cursos por su nombre.
    # La entrada es el nombre del curso, y la función devuelve
    # una lista de cursos cuyos nombres coinciden con la entrada.

    # Encontrar un match por si esta traducido o escrito de forma diferente
    course_name = find_course_name(argument)

    resultados = get_course_by_name_fetch(course_name)  # Función original
    if not resultados:
        return f"There are no courses with the name {argument}."

    descripcion = f"I found the following course: '{argument}':\n"
    for curso in resultados:
        descripcion += (
            f"- Course: {curso['nombre']} (ID: {curso['id_curso']}), "
            f"Description: {curso['descripcion']}.\n"
        )
    return descripcion

# Función para buscar curso por código y retornar en lenguaje natural
# Redireccion: SI. a get_course_by_name
def get_course_by_code(argument: str) -> str:
    """
    Searches for courses by their code.
    The input is the course code, and the function returns
    a list of courses whose codes match the input.
    
    :param argument: The code of the course to search for.
    :return: A list of dictionaries representing courses whose codes match the input.
    
    Example call:
    get_course_by_code("CS101")
    """

    # Si el argumento es una palabra, redirigir a get_course_by_name
    if not argument.isdigit():
        print("[DBSearch] received a word, redirecting to get_course_by_name")
        return get_course_by_name(argument)

    print(f"[DBSearch] Searching for course with code: {argument}")
    resultados = get_course_by_code_fetch(argument)  # Llamada a la función fetch
    if not resultados:
        return f"There are no courses with the code {argument}."

    descripcion = f"I found the following course: '{argument}':\n"
    for curso in resultados:
        descripcion += (
            f"- Course: {curso['nombre']} (ID: {curso['id_curso']}), "
            f"Description: {curso['descripcion']}.\n"
        )
    return descripcion


# Función para buscar clases por código de curso y retornar en lenguaje natural
# Redireccion: SI. a get_classes_by_course_name
def get_classes_by_course_code(argument: str) -> str:
    """
    Searches for classes by course code.
    The input is the course code, and the function returns
    a list of classes associated with that course code.
    
    :param argument: The code of the course to search for.
    :return: A list of dictionaries representing classes associated with the given course code.
    
    Example call:
    get_classes_by_course_code("1511")
    """

    # Si el argumento es una palabra, redirigir a get_classes_by_course_name
    if not argument.isdigit():
        print("[DBSearch] received a word, redirecting to get_classes_by_course_name")
        return get_classes_by_course_name(argument)

    # Busca clases por el código del curso.
    # La entrada es el código del curso, y la función devuelve
    # una lista de clases asociadas con ese código de curso.
    resultados = get_classes_by_course_code_fetch(argument)  # Función original
    if not resultados or len(resultados) < 2:
        return f"There are no classes for the course with code '{argument}'."

    # El primer elemento es la información del curso, así que lo omitimos
    descripcion = f"There are {len(resultados) - 1} classes for the course with code '{argument}':\n"
    for clase in resultados[1:]:  # Empezamos desde el segundo elemento
        descripcion += (
            f"- Class ID: {clase['id_clase']}, "
            f"period: {clase['periodo']}, "
            f"from {clase['fecha_inicio']} to {clase['fecha_final']}.\n"
        )
    return descripcion

# Función para buscar clases por nombre de curso y retornar en lenguaje natural
# Redireccion: SI. a get_classes_by_course_code
def get_classes_by_course_name(argument: str) -> str:
    """
    Searches for classes by course name.
    The input is the course name, and the function returns
    a list of classes associated with that course name.
    
    :param argument: The name of the course to search for.
    :return: A list of dictionaries representing classes associated with the given course name.
    
    Example call:
    get_classes_by_course_name("Mathematics")
    """

    # Si el argumento es un número, redirigir a get_classes_by_course_code
    if argument.isdigit():
        print("[DBSearch] received a number, redirecting to get_classes_by_course_code")
        return get_classes_by_course_code(argument)

    # Busca clases por el nombre del curso.
    # La entrada es el nombre del curso, y la función devuelve
    # una lista de clases asociadas con ese nombre de curso.

    # Encontrar un match por si esta traducido o escrito de forma diferente
    course_name = find_course_name(argument)

    resultados = get_classes_by_course_name_fetch(course_name)  # Función original
    if not resultados:
        return f"There are no classes for the course '{argument}'."

    descripcion = f"I found {len(resultados)} classes for the course '{argument}':\n"
    for clase in resultados:
        descripcion += (
            f"- Class ID: {clase['id_clase']}, "
            f"period: {clase['periodo']}, "
            f"from {clase['fecha_inicio']} to {clase['fecha_final']}.\n"
        )
    return descripcion

# Función para buscar clase por código y retornar en lenguaje natural
# Redireccion: NO
def get_class_by_code(argument: str) -> str:
    """
    Searches for a class by its code.
    The input is the class code, and the function returns
    details of the class with that code.
    
    :param argument: The code of the class to search for.
    :return: A list of dictionaries representing the class details.
    
    Example call:
    get_class_by_code("1511")
    """
    # Busca una clase por su código.
    # La entrada es el código de la clase, y la función devuelve
    # detalles de la clase con ese código.
    resultados = get_class_by_code_fetch(argument)  # Función original
    if not resultados:
        return f"There are no classes with the code '{argument}'."

    descripcion = f"I found a class with code '{argument}':\n"
    for clase in resultados:
        descripcion += (
            f"- Class ID: {clase['id_clase']}, "
            f"corresponding to course ID: {clase['id_curso']}, "
            f"period: {clase['periodo']}, "
            f"from {clase['fecha_inicio']} to {clase['fecha_final']}.\n"
        )
    return descripcion

# Función para buscar prerrequisitos por nombre de curso y retornar en lenguaje natural
# Redireccion: SI. a get_prerequisites_by_course_code
def get_prerequisites_by_course_name(argument: str) -> str:
    """
    Searches for prerequisites of a course by course name.
    The input is the course name, and the function returns
    a list of prerequisites for that course.
    
    :param argument: The name of the course to search for prerequisites.
    :return: A list of dictionaries representing prerequisites for the course.
    
    Example call:
    get_prerequisites_by_course_name("Mathematics")
    """

    # If the received args contain a number and not only letters
    if argument.isdigit():
        print("[DBSearch] received a number, redirecting to get_prerequisites_by_course_code")
        return get_prerequisites_by_course_code(argument)

    # Busca prerrequisitos de un curso por nombre del curso.
    # La entrada es el nombre del curso, y la función devuelve
    # una lista de prerrequisitos para ese curso.

    # Encontrar un match por si esta traducido o escrito de forma diferente
    course_name = find_course_name(argument)

    resultados = get_prerequisites_by_course_name_fetch(course_name)  # Función original
    if not resultados:
        return f"There are no prerequisites for the course '{argument}'."

    descripcion = f"There are {len(resultados)} prerequisites for the course '{argument}':\n"
    for prerrequisito in resultados:
        descripcion += f"- {prerrequisito['curso_prerrequisito']}.\n"
    return descripcion

# Función para buscar prerrequisitos por código de curso y retornar en lenguaje natural
# Redireccion: SI. a get_prerequisites_by_course_name
def get_prerequisites_by_course_code(argument: str) -> str:
    """
    Searches for prerequisites of a course by course code.
    The input is the course code, and the function returns
    a list of prerequisites for that course.
    
    :param codigo_curso: The code of the course for which prerequisites are to be searched.
    :return: A list of dictionaries representing prerequisites for the given course code.
    
    Example call:
    get_prerequisites_by_course_code("1511")
    """

    # If the received args contain a letters and not only numbers
    if not argument.isdigit():
        print("[DBSearch] Received argument is not a number. Redirecting to get_prerequisites_by_course_name.")
        return get_prerequisites_by_course_name(argument)

    # Busca prerrequisitos de un curso por código del curso.
    # La entrada es el código del curso, y la función devuelve
    # una lista de prerrequisitos para ese curso.
    resultados = get_prerequisites_by_course_code_fetch(argument)  # Función original
    if not resultados:
        return f"There are no prerequisites for the course with code '{argument}'."

    descripcion = f"There are {len(resultados)} prerequisites for the course with code '{argument}':\n"
    for prerrequisito in resultados:
        descripcion += f"- {prerrequisito['curso_prerrequisito']}.\n"
    return descripcion


# Función para obtener horarios de clases y retornar en lenguaje natural
# Redireccion: NO
def get_class_schedule(argument: str) -> str:
    """
    Searches for the schedule(s) of a class by its class ID.
    The function returns the schedule(s) for the specified class.
    
    :param argument: A single class ID to search for its schedule(s).
    :return: A description of the schedule(s) for the specified class.
    
    Example call:
    get_class_schedule("1511")
    """
    # Busca los horarios de una clase por su ID.
    resultado = get_class_schedule_fetch(argument)
    if not resultado:
        return "I am sorry, no schedules were found for the specified class."

    descripcion = f"This are the schedules for class with ID {argument}:\n"
    for horario in resultado:
        descripcion += (
            f"- Day: {horario['dia']}, "
            f"from {horario['hora_inicio']} to {horario['hora_fin']}.\n"
        )
    return descripcion

# Función para buscar profesor por nombre y retornar en lenguaje natural
# Redireccion: NO
def get_teacher_by_name(argument: str) -> str:
    """
    Searches for professors by their name.
    The input is the professor's name, and the function returns
    a list of professors whose names match the input.
    
    :param argument: The name of the professor to search for.
    :return: A description of professors whose names match the input.
    
    Example call:
    get_teacher_by_name("Carlos")
    """
    # Busca profesores por su nombre.
    # La entrada es el nombre del profesor, y la función devuelve
    # una lista de profesores cuyos nombres coinciden con la entrada.
    resultados = get_teacher_by_name_fetch(argument)  # Función original
    if not resultados:
        return f"There are no professors with the name {argument}."

    descripcion = f"There are {len(resultados)} professors with the name '{argument}':\n"
    for profesor in resultados:
        descripcion += (
            f"- {profesor['nombres']} {profesor['apellidos']} (ID: {profesor['id_profesor']}), "
            f"Email: {profesor['email']}, "
            f"Phone: {profesor['telefono']}.\n"
        )
    return descripcion
