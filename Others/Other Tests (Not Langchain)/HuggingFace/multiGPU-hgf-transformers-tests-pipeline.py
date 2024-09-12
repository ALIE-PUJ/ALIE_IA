from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextStreamer
import torch
from torch import cuda, bfloat16
import time

# Importante instalar pytorch con CUDA para usar la GPU (Necesario para cuantizar): https://pytorch.org/get-started/locally/

# MultiGPU Config. 4 GPU (Max alloc: 2.5GB per GPU (VRAM))
max_memory_mapping = {0: "2.5GB", 1: "2.5GB", 2: "2.5GB", 3: "2.5GB"}

# Con Transformers AutoModelForCausalLM
# Código base obtenido de https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct

def get_device_info():
    print("Device information")
    print("Cuda availability: ", torch.cuda.is_available())

    # Verificar si CUDA está disponible
    if cuda.is_available():
        print("Main")
        print("Cuda Device: ", cuda.current_device())
        device_name = torch.cuda.get_device_name(cuda.current_device())
    else:
        device_name = "CPU"

    print("Current device: ", device_name)

    # Check if CUDA is available
    if torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        print(f"\nNumber of available GPUs: {num_gpus}")
        for i in range(num_gpus):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")

        print("\n")
    else:
        print("CUDA is not available. Using CPU.")


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
    device_map="auto",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True), # Cargar en 4 bits,
    max_memory=max_memory_mapping # Repartir la memoria entre los 4 GPU
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

# Streaming config
# streamer = TextStreamer(tokenizer)
# output = model.generate(**inputs, streamer=streamer, max_new_tokens=20)

# Terminar de medir el tiempo de ejecución
end_time = time.time()

# Calcular y mostrar el tiempo total de ejecución
total_time = end_time - start_time
print(f"El tiempo de ejecución fue de {total_time} segundos")
