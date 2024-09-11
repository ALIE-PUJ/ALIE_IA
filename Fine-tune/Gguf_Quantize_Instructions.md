# Instrucciones para conversión a gguf y cuantización

## Importante. Se requiere la previa descarga de Llama.cpp para poder usar dichos .py. Llama.cpp está disponible en: https://github.com/ggerganov/llama.cpp

Para convertir un modelo descargado con download_models.py, usar el siguiente comando (Cambiar con la ubicación de su directorio):
python llama.cpp\convert_hf_to_gguf.py "C:\Users\Luis Alejandro\Desktop\AI_ML\Models\Downloaded models\Meta-Llama-3-8B-Instruct"   --outfile llama3_8b_test.gguf  --outtype q8_0

(--outtype q8_0 Cuantiza a 8 bits)

Se puede dejar con --outtype f16 o --outtype f32 para preservar la calidad original del modelo y posteriormente utilizar quantize (También disponible en Llama.cpp) para cuantizarlo a 4 bits.