import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import random
from datasets import load_dataset


### with schema in the prompts
def get_schema_context(db_id):
    """
    In a real app, we pull this from a metadata dictionary or SQLITE_MASTER.
    For this benchmark, we can look at the 'db_id' and provide the tables.
    """
    # Example schema format that Qwen2.5 excels at but this is not the real schema (tech debt)
    if db_id == "concert_singer":
        return """
        Table conductor (Conductor_ID, Name, Age, Nationality, Year_of_Work)
        Table orchestra (Orchestra_ID, Name, Rating, Conductor_ID, Type)
        """
    # Add other DBs or a generic fetcher here
    return ""

def get_prompt_with_schema(example):
    db_id = example['db_id']
    question = example['question']
    # tech debt: need to pull exact schema from a real database to inject it into the prompt
    schema = get_schema_context(db_id)
    
    if len(schema.strip()) == "" :
        return f"<|im_start|>system\nYou are a SQL expert. Output Postgres SQL only.<|im_end|>\n<|im_start|>user\nDatabase: {example['db_id']}\nQuestion: {example['question']}\nSQL Output:<|im_end|>\n<|im_start|>assistant\n"
    return  f"""<|im_start|>system
You are a SQL expert. Use the provided database schema to write a clean Postgres SQL query.
<|im_end|>
<|im_start|>user
Schema:
{schema}

Question: {question}
SQL Output:<|im_end|>
<|im_start|>assistant
"""
   
###

# 1. Load the Model & Tokenizer
# Use the same base model that was used for training (e.g., Qwen/Qwen2.5-3B-Instruct)
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct" # "Qwen/Qwen2.5-3B-Instruct" 
ADAPTER_PATH = ".model/llmsqler-final"
TOKENIZER_PATH = ".model/llmsqler_v1/checkpoint-300"

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

# 2. Load Get Test Data
# Load the raw dataset
raw_dataset = load_dataset("xlangai/spider", split="validation")

# Apply the tokenizer
# do not format into 'prompt' and 'completion' columns
eval_dataset = raw_dataset #.map(format_dataset, remove_columns=raw_dataset.column_names)


print("\n--- Starting SQL Benchmark ---")

def run_test(example):
    prompt = get_prompt_with_schema(example)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=100,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
            do_sample=False # Greedy decoding for reproducible results
        )
    
    # Extract only the newly generated text
    generated_text = tokenizer.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
    return generated_text.strip()

# Pick 5 random questions to test
test_indices = random.sample(range(len(eval_dataset)), 5)

for i in test_indices:
    item = eval_dataset[i] # Use raw split to get 'db_id' and 'question' easily       
    gold_sql = item['query']
    pred_sql = run_test(item) 
    
    print(f"\n[Question]: {item['question']}")
    print(f"[Gold SQL]: {gold_sql}")
    print(f"[Pred SQL]: {pred_sql}")
    print("-" * 30)