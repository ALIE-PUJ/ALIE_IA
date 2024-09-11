from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.agents import tool

# Importar libreria propia
from Library.DBsearchTests_Library import *

import getpass
import os

# Definir el modelo


# Opcion 1: Definicion manual del pipeline.
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline # pip install langchain_huggingface
import torch

'''
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True) # 4-bit quantization
)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=1000, top_k=50, temperature=0.1)
llm = HuggingFacePipeline(pipeline=pipe)
'''

'''
# Opcion 2: Definicion automatica del pipeline.
llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/Phi-3-mini-4k-instruct",
    task="text-generation",
    pipeline_kwargs={
        "max_new_tokens": 100000,
        "top_k": 50,
        "temperature": 0.1,
    },
)
'''



model_id = "microsoft/Phi-3-mini-4k-instruct"
model_id = "google/gemma-2-2b-it"

tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True) # 4-bit quantization
)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=1000, top_k=50, temperature=0.1)
llm = HuggingFacePipeline(pipeline=pipe)



# Endpoint gratis de HuggingFace (Limitado)
'''
from langchain_huggingface import HuggingFaceEndpoint
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    max_new_tokens=1000,
    do_sample=False,
)
'''

# Inicializar el agente
agent= initialize_agent(
    [get_students_by_name,
     get_course_by_name,
     get_classes_by_course_code,
     get_classes_by_course_name,
     get_class_by_code,
     get_prerequisites_by_course_code,
     get_prerequisites_by_course_name,
     get_class_schedule,
     get_teacher_by_name], 
    llm, 
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, # Se pueden usar varios tipos. Probar
    handle_parsing_errors=True,
    verbose = True,
    max_execution_time=30 # Tiempo máximo de ejecución (En segundos)
    )


# Q&A
question1 = "Is there any student called Luis? Who?"
question2 = "Which is the course code for Estructuras de datos?" # Hay que remover las tildes de las inserciones SQL.
question3 = "Which are the available classes for the course with code 4196?"
question4 = "Which are the available classes for the Estructuras de datos course? Give me their codes"
question5 = "Which are the prerequisites for Estructuras de datos?"
question6 = "Which are the prerequisites for the course with code 4196?"
question7 = "Which are the available schedules for class 1557?"
question8 = "Are there any teachers called Oscar? Who?"

result = agent(question8) 
print("Answer: ", result)

# Si se queda en un bucle de "Pensamiento" hay que hacer manejo de errores