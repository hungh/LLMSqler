from qwen_ft import tokenizer
import torch
# from datasets import load_dataset 

# load spider original dataset from HF
# spider = load_dataset("xlangai/spider", split="train")

# the spider ds with columns below
# db_id, query, question, query_toks, query_toks_no_value, question_toks

# For examnple (by column)

# department_management
# SELECT count(*) FROM head WHERE age > 56
# How many heads of the departments are older than 56 ?

# [ "SELECT", "count", "(", "*", ")", "FROM", "head", "WHERE", "age", ">", "56" ]

# [ "select", "count", "(", "*", ")", "from", "head", "where", "age", ">", "value" ]

# [ "How", "many", "heads", "of", "the", "departments", "are", "older", "than", "56", "?" ]

def format_dataset(example):
   # Construct the prompt (schema + question)
    # We use Qwen's ChatML-style headers for consistency
    prompt = f"<|im_start|>system\nYou are a SQL expert. Output Postgres SQL only.<|im_end|>\n<|im_start|>user\nDatabase: {example['db_id']}\nQuestion: {example['question']}\nSQL Output:<|im_end|>\n"
    
    # The completion is the gold-standard SQL
    completion = f"<|im_start|>assistant\n{example['query']}<|im_end|>"
    
    return {"prompt": prompt, "completion": completion}

### deprecated
def tokenize_function(examples):
    print(f"Processing {len(examples['question'])} examples")
    texts = []
    i = 0
    for q, db, sql in zip(examples['question'], examples['db_id'], examples['query']):
        if not q or not db or not sql:
            continue
        # 2. Construct a professional 'Agentic' prompt
        # We include the db_id so the model knows which 'domain' it is in.
        prompt = f"### Database: {db}\n### Question: {q}\n### SQL Output:"
 
        # 3. Format using Qwen's Chat Template
        messages = [
            {"role": "system", "content": "You are a text-to-SQL expert. Output valid Postgres SQL only."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": sql}
        ]
        
        # Apply template but do NOT tokenize yet so we can batch process
        texts.append(tokenizer.apply_chat_template(messages, tokenize=False))

        if i % 100 == 0:
            print(f"Sample prompt: {texts[i][:100]}...")
        i += 1

    # 4. Final Tokenization (This is where sub-word splitting happens)
    model_inputs = tokenizer(
        texts, 
        max_length=2048, 
        truncation=True, 
        padding="max_length"
    )
    
    print(f"Tokenized input shape: {model_inputs['input_ids'].shape}")
    # Labels are crucial: the model needs to predict the next token
    model_inputs["labels"] = model_inputs["input_ids"].copy()

    return model_inputs