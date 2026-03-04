# Spider dataset columns and examples 
# db_id, query, question, query_toks, query_toks_no_value, question_toks
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
