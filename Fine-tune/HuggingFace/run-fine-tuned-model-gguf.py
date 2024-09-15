from llama_cpp import Llama

# pip install llama-cpp-python

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = Llama(
  model_path="Fine-tune\Gguf output\Meta-Llama-3-8B-Instruct-medical_qa-Finetune.gguf", 
  n_ctx=32768,  # The max sequence length to use - note that longer sequence lengths require much more resources
  n_threads=1,            # The number of CPU threads to use, tailor to your system and the resulting performance
  n_gpu_layers=-1         # The number of layers to offload to GPU, if you have GPU acceleration available
)

query = """Please answer with one of the option in the bracket. Write reasoning in between <analysis></analysis>. Write answer in between <answer></answer>. here are the inputs Q:An 8-year-old boy is brought to the pediatrician by his mother with nausea, vomiting, and decreased frequency of urination. He has acute lymphoblastic leukemia for which he received the 1st dose of chemotherapy 5 days ago. His leukocyte count was 60,000/mm3 before starting chemotherapy. The vital signs include: pulse 110/min, temperature 37.0°C (98.6°F), and blood pressure 100/70 mm Hg. The physical examination shows bilateral pedal edema. Which of the following serum studies and urinalysis findings will be helpful in confirming the diagnosis of this condition? ? \n{'A': 'Hyperkalemia, hyperphosphatemia, hypocalcemia, and extremely elevated creatine kinase (MM)', 'B': 'Hyperkalemia, hyperphosphatemia, hypocalcemia, hyperuricemia, urine supernatant pink, and positive for heme', 'C': 'Hyperuricemia, hyperkalemia, hyperphosphatemia, lactic acidosis, and urate crystals in the urine', 'D': 'Hyperuricemia, hyperkalemia, hyperphosphatemia, and urinary monoclonal spike', 'E': 'Hyperuricemia, hyperkalemia, hyperphosphatemia, lactic acidosis, and oxalate crystals'}"""
output = llm(
  prompt=query,
  max_tokens=512,  # Generate up to 512 tokens
)

print(output)