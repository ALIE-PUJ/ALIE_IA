# Local Agent imports (Library)
from Local_Agent.LmStudio_LocalFunctionCallAgent import *

# Define constants and run the functions
api_url = "http://127.0.0.1:1234/v1/chat/completions"

# Define the content of the user input as a modifiable string
question1 = "Is there any student called Luis? Who?"
question2 = "Which is the course code for the course named 'Estructuras de datos'?" # Hay que remover las tildes de las inserciones SQL.
question3 = "Which are the available classes for the course with code 4196?"
question4 = "Which are the available classes for the Estructuras de datos course? Give me their codes"
question5 = "Which are the prerequisites for Estructuras de datos?"
question6 = "Which are the prerequisites for the course with code 4196?"
question7 = "Which are the available schedules for class 1557?"
question8 = "Are there any teachers called Carlos? Who?"

user_input = question8

# Run the function call and generate the final response
process_user_query(user_input, api_url)