import os

# Importe de librerias de herramientas
from RelationalDB.DBsearchTests_Library import *

def write_output_file(text):
    # Guardar resultados en un archivo en el mismo directorio del script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    result_file_path = os.path.join(current_directory, 'Tests_output.txt')

    # Abrir el archivo en modo "a" para agregar el contenido en lugar de sobrescribirlo
    with open(result_file_path, "a", encoding="utf-8") as file:
        file.write(text + "\n\n")  # Agregar dos nuevas líneas después de cada entrada


if __name__ == "__main__":
    # Reiniciar el archivo al comienzo del script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    result_file_path = os.path.join(current_directory, 'Tests_output.txt')
    
    # Abrir en modo "w" al principio para limpiar el contenido
    open(result_file_path, "w").close()

    # Pruebas de las distintas herramientas

    result = get_students_by_name("Luis")
    write_output_file("get_students_by_name:\n" + result)

    result = get_course_by_name("Calculo vectorial")
    write_output_file("get_course_by_name:\n" + result)

    result = get_course_by_code("4196")
    write_output_file("get_course_by_code:\n" + result)

    result = get_classes_by_course_code("4196")
    write_output_file("get_classes_by_course_code:\n" + result)

    result = get_classes_by_course_name("Calculo diferencial")
    write_output_file("get_classes_by_course_name:\n" + result)

    result = get_class_by_code("528")
    write_output_file("get_class_by_code:\n" + result)

    result = get_prerequisites_by_course_name("Estructuras de datos")
    write_output_file("get_prerequisites_by_course_name:\n" + result)

    result = get_prerequisites_by_course_code("4196")
    write_output_file("get_prerequisites_by_course_code:\n" + result)

    result = get_class_schedule("528")
    write_output_file("get_class_schedule:\n" + result)

    result = get_teacher_by_name("Oscar")
    write_output_file("get_teacher_by_name:\n" + result)

    result = get_student_grades_by_period("1")
    write_output_file("get_student_grades_by_period:\n" + result)

    result = get_student_courses("1")
    write_output_file("get_student_courses:\n" + result)

    result = get_all_courses("")
    write_output_file("get_all_courses:\n" + result)

    result = get_student_classes("1")
    write_output_file("get_student_classes:\n" + result)





    # Añadir al agente. Retorno directo.
    result = get_student_academic_summary("1")
    write_output_file("get_student_academic_summary:\n" + result)


    # Cumplimiento de RFs
    '''
    RF 2. Permitir consultas personalizadas sobre calificaciones y clases. HECHO
    RF 2.1. El sistema debe contestar consultas sobre las calificaciones definitivas de las clases inscritas de un usuario autenticado. HECHO
    RF 2.2. El sistema debe poder contestar consultas sobre la base de información de las clases inscritas en el semestre actual, como los documentos de la clase, el temario del curso, entre otros. HECHO
    ****RF 2.3. El sistema debe poder contestar consultas sobre las asignaturas pendientes por ver del plan de estudios. FALTANTE.
    RF 2.4. El sistema debe poder sugerir asignaturas electivas, que le sirvan al estudiante para inscribir según sus condiciones de requisitos. HECHO (RAG)
    RF 2.5. El sistema debe poder contestar consultas sobre los horarios de las clases inscritas y disponibles para inscribir. HECHO
    '''