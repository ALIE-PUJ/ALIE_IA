import transformers
import torch
from torch import cuda, bfloat16
import time

# Importante instalar pytorch con CUDA para usar la GPU (Necesario para cuantizar): https://pytorch.org/get-started/locally/

# Instalaciones
# pip install transformers
# pip install torch
# pip install bitsandbytes
# Para instalar con CUDA: pip3 install torch==2.2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Con Transformers pipeline
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

# 1. Base. Sin cuantización
'''
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto", # Seleccionar el dispositivo automáticamente (GPU si está disponible)
)
'''

# 2. Cuantización de 4 bits
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={
    "torch_dtype": torch.bfloat16,
    "quantization_config": {"load_in_4bit": True}, # Cargar en 4 bits *(cuantización)
    "low_cpu_mem_usage": True, # Reducir el uso de memoria en CPU
    },
    device_map="auto",  # Para ponerlo en GPU, usar "cuda". Si no, "auto" encontrara la mejor opción para el dispositivo
)

# Obtener el modelo subyacente
model = pipeline.model

# Imprimir el dispositivo utilizado por el modelo
print(f"El modelo está utilizando el dispositivo: {model.device}...\n")

# Historial de mensajes
messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

# Iniciar a medir el tiempo de ejecución
start_time = time.time()

# Generar la respuesta
outputs = pipeline(
    messages,
    max_new_tokens=256,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
)
# Imprimir la respuesta generada
print(outputs[0]["generated_text"][-1])

# Terminar de medir el tiempo de ejecución
end_time = time.time()

# Calcular y mostrar el tiempo total de ejecución
total_time = end_time - start_time
print(f"El tiempo de ejecución fue de {total_time} segundos")