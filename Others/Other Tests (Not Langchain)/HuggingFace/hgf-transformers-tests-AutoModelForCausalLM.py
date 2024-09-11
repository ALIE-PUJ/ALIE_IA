from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from torch import cuda, bfloat16
import time

# Con Transformers AutoModelForCausalLM
# Código base obtenido de https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct

def get_device_info():
    print("Device information")
    print("Cuda availability: ", torch.cuda.is_available())

    # Verificar si CUDA está disponible
    if cuda.is_available():
        print("Cuda Device: ", cuda.current_device())
        device_name = torch.cuda.get_device_name(cuda.current_device())
    else:
        device_name = "CPU"

    print("Current device: ", device_name)

# Obtener información del dispositivo
get_device_info()

# Modelo a utilizar
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# Configuraciones del modelo
tokenizer = AutoTokenizer.from_pretrained(model_id)

'''
# 1. Base. Sin cuantización
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
'''

# 2. Con cuantización, 4 bits
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",  # Para ponerlo en GPU, usar "cuda". Si no, "auto" encontrara la mejor opción para el dispositivo
    quantization_config=BitsAndBytesConfig(load_in_4bit=True)
)

# Imprimir el dispositivo utilizado por el modelo
print(f"El modelo está utilizando el dispositivo: {model.device}...\n")

# Historial de mensajes
messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

input_ids = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt"
).to(model.device)

terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

# Iniciar a medir el tiempo de ejecución
start_time = time.time()

outputs = model.generate(
    input_ids,
    max_new_tokens=256,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
)
response = outputs[0][input_ids.shape[-1]:]
print(tokenizer.decode(response, skip_special_tokens=True))

# Terminar de medir el tiempo de ejecución
end_time = time.time()

# Calcular y mostrar el tiempo total de ejecución
total_time = end_time - start_time
print(f"El tiempo de ejecución fue de {total_time} segundos")