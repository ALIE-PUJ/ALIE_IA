import time

# Local Agent imports (Library)
from Local_Agent.LmStudio_LocalFunctionCallAgent import *

def call_process_user_query_with_retries(user_input, api_url, max_retries=3, delay=1):
    """
    Calls process_user_query and retries if the result is None.
    
    :param user_input: The input query from the user.
    :param api_url: The URL of the API to send requests to.
    :param max_retries: Maximum number of retries if the result is None (default 3).
    :param delay: Delay between retries in seconds (default 1).
    :return: The result of process_user_query or None if all retries fail.
    """
    retries = 0
    answer = None
    start_time = time.time()  # Start the timer
    
    while retries < max_retries:
        answer = process_user_query(user_input, api_url)
        
        if answer is not None:
            end_time = time.time()  # End the timer
            elapsed_time = end_time - start_time
            print(f"[INFO] Successful on attempt {retries + 1}. Execution time: {elapsed_time:.2f} seconds.")
            return answer  # Exit loop if a valid answer is returned
        
        retries += 1
        print(f"[INFO] Attempt {retries} returned None. Retrying in {delay} seconds...")
        time.sleep(delay)

    # If all retries failed
    end_time = time.time()  # End the timer after final attempt
    elapsed_time = end_time - start_time
    print(f"Max retries reached. Total execution time: {elapsed_time:.2f} seconds.")
    return None  # Return None if all retries fail

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
question8 = "Are there any teachers called Oscar? Who?"

user_input = question8

# Run the function call and generate the final response
answer = call_process_user_query_with_retries(user_input, api_url)
print("\n[Response] ---> Answer = ", answer)