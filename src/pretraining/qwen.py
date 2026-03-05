import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct" # "Qwen/Qwen2.5-3B-Instruct" 
ADAPTER_PATH = ".model/llmsqler-final"
TOKENIZER_PATH = ".model/llmsqler_v1/checkpoint-300"

def model_and_tokenizer():
    # local tokenizer
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, 
        device_map="auto", 
        torch_dtype=torch.bfloat16
    )
    # Load local LoRA weights on top
    model = PeftModel.from_pretrained(model, ADAPTER_PATH, use_fast=False)
    model.eval()
    return model, tokenizer