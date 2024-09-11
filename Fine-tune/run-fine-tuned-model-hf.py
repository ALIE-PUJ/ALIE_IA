from peft import LoraConfig,PeftModel,AutoPeftModelForCausalLM
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

#set the LoRA configurations
peft_config =LoraConfig(
    r=64,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
#

peft_model_id = "Fine-tune\Meta-Llama-3-8B-Instruct-medical_qa-Finetune" # Should be the local model path

config = peft_config.from_pretrained(peft_model_id)

model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path,
                                             return_dict=True,
                                             load_in_4bit=True,
                                             device_map="auto",
                                             )
ptokenizer= AutoTokenizer.from_pretrained(peft_model_id)

# Helper function
def get_completion(query: str, model, tokenizer) -> str:
  device = "cuda:0"

  prompt_template = """
  <start_of_turn>user
  Below is an instruction that describes a task. Write a response that appropriately completes the request.
  {query}
  <end_of_turn>\n<start_of_turn>model


  """
  prompt = prompt_template.format(query=query)

  encodeds = tokenizer(prompt, return_tensors="pt", add_special_tokens=True)

  model_inputs = encodeds.to(device)


  generated_ids = model.generate(**model_inputs, max_new_tokens=1000, do_sample=True, pad_token_id=tokenizer.eos_token_id)
  # decoded = tokenizer.batch_decode(generated_ids)
  decoded = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
  return (decoded)


# Example medical query

query = """Please answer with one of the option in the bracket. Write reasoning in between <analysis></analysis>. Write answer in between <answer></answer>.here are the inputs:Q:A 34-year-old man presents to a clinic with complaints of abdominal discomfort and blood in the urine for 2 days. He has had similar abdominal discomfort during the past 5 years, although he does not remember passing blood in the urine. He has had hypertension for the past 2 years, for which he has been prescribed medication. There is no history of weight loss, skin rashes, joint pain, vomiting, change in bowel habits, and smoking. On physical examination, there are ballotable flank masses bilaterally. The bowel sounds are normal. Renal function tests are as follows:\nUrea 50 mg/dL\nCreatinine 1.4 mg/dL\nProtein Negative\nRBC Numerous\nThe patient underwent ultrasonography of the abdomen, which revealed enlarged kidneys and multiple anechoic cysts with well-defined walls. A CT scan confirmed the presence of multiple cysts in the kidneys. What is the most likely diagnosis?? \n{'A': 'Autosomal dominant polycystic kidney disease (ADPKD)', 'B': 'Autosomal recessive polycystic kidney disease (ARPKD)', 'C': 'Medullary cystic disease', 'D': 'Simple renal cysts', 'E': 'Acquired cystic kidney disease'}"""
result = get_completion(query=query, model=model, tokenizer=ptokenizer)
print(f"Model Answer : \n {result}")
