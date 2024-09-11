from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.agents import tool
from datetime import date

# Definir el modelo
llm = ChatOpenAI(
    model="llama3:latest",
    temperature=0.9,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    base_url="http://localhost:11434/v1/",
    api_key="ollama"    # organization="...",
    # other params...
)

# Herramientas
tools = load_tools(["llm-math","wikipedia"], llm=llm)
@tool
def time(text: str) -> str:
    """Returns todays date and hour, use this for any \
    questions related to knowing todays date. \
    The input should always be an empty string, \
    and this function will always return todays \
    date - any date mathmatics should occur \
    outside this function."""
    return str(date.today())

from mysql.connector import connect, Error
@tool
def search_person_info_by_name(first_name: str) -> str:
    """
    Look up a person's information by their first name in the MySQL database. 
    It receives a string with the person's first name.
    The available information is: nombre, apellido, edad, ciudad, carrera, gustos, comida_favorita
    """
    print("Received first name: ", first_name)
    try:
        connection = connect(
            host="localhost",
            user="root",
            password="1234",
            database="langchain_db_tests"
        )
        cursor = connection.cursor()
        query = f"SELECT * FROM personas WHERE nombre = '{first_name}'"
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result_with_columns = [dict(zip(columns, row)) for row in result]
        cursor.close()
        connection.close()
        return str(result_with_columns)
    except Error as e:
        return f"Error: {e}"

# Inicializar el agente
agent= initialize_agent(
    tools  + [time, search_person_info_by_name], 
    llm, 
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose = True)


# Q&A
question = "Tom M. Mitchell is an American computer scientist \
and the Founders University Professor at Carnegie Mellon University (CMU)\
what book did he write?"

question = "Cual es la comida favorita de Juan??"

final_question = question + "\nResponde de manera amable al usuario, en la menor cantidad de pasos posibles"

result = agent(final_question) 
print("Answer: ", result)

# Si se queda en un bucle de "Pensamiento" hay que hacer manejo de errores