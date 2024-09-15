Para realizar fine-tuning con autotrain, seguir las instrucciones de: https://github.com/huggingface/autotrain-advanced
Una vez se ha levantado el servidor en una máquina cuda-compatible, al entrar a 127.0.0.1 podrá seleccionar el modelo base, y realizar el fine-tuning con los datos de un CSV con un campo "text", preferiblemente (Es donde se encuentran los datos que se usarán para entrenar).

Desventaja: Dado a que solo genera los adaptadores LoRA y no sube el modelo completo, hay que hacer la mezcla a mano, lo cual complifica el proceso para convertir en .gguf