from langchain_community.llms import Ollama

# Crear una instancia del modelo Llama3
llm = Ollama(
    model="llama3"
)  # assuming you have Ollama installed and have llama3 model pulled with `ollama pull llama3 `

while True:
    # Solicitar al usuario que ingrese su pregunta
    query = input("Escribe tu pregunta (o 'salir' para terminar): ")

    # Salir del bucle si el usuario escribe 'salir'
    if query.lower() == 'salir':
        print("Adiós!")
        break

    # Usar la pregunta del usuario para generar la respuesta
    for chunk in llm.stream(query):
        print(chunk, end="", flush=True)

    # Línea en blanco para mejorar la legibilidad entre respuestas
    print("\n")
