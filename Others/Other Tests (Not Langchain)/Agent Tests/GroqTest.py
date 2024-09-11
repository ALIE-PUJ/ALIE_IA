from groq import Groq
import os
# pip install groq

api_key = os.getenv("GROQ_API_KEY", "NotFound") # Obtener la API Key de las variables de entorno
client = Groq(api_key=api_key)
completion = client.chat.completions.create(
    model="llama3-groq-70b-8192-tool-use-preview",
    messages=[
        {
            "role": "user",
            "content": "Hi!"
        }
    ],
    temperature=0.5,
    max_tokens=1024,
    top_p=0.65,
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")