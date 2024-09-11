from huggingface_hub import snapshot_download

# https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
repo_id = "meta-llama/Meta-Llama-3-8B-Instruct"
snapshot_download(repo_id, local_dir="C:/Users/Luis Alejandro/Desktop/AI_ML/Models/Downloaded models/Meta-Llama-3-8B-Instruct") # Change with your local directory