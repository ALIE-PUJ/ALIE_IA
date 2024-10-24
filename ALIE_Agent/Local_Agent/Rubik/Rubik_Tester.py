# Library import depending on the context (Being used as a library or being executed directly)
if __name__ == "__main__":
    # Direct execution, absolute import
    from Rubik_Main import *
else:
    # Imported as part of a package, relative import
    from .Rubik_Main import *

if __name__ == "__main__":
    student_id = 3
    rubik_text = rubik(student_id)
    print("RUBIK ANSWER:")
    print(rubik_text)

    # Guardar resultados en un archivo en el mismo directorio del script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    result_file_path = os.path.join(current_directory, 'Rubik_output.txt')

    # Write the result to the file in the current location
    with open(result_file_path, "w", encoding="utf-8") as file:
        file.write(rubik_text)
