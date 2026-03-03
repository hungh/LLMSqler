import torch

def test_live_model(question, db_id="college_1"):
    model.eval() # Set to inference mode
    
    # Format exactly like the training data
    prompt = f"<|im_start|>system\nYou are a SQL expert. Output Postgres SQL only.<|im_end|>\n"
    prompt += f"<|im_start|>user\nDatabase: {db_id}\nQuestion: {question}\nSQL Output:<|im_end|>\n<|im_start|>assistant\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=100,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id
        )
    
    # Clean up the output to see just the SQL
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    sql = decoded.split("assistant\n")[-1].strip()
    
    model.train() # Set back to training mode
    return sql

# Try a classic Spider question
print(f"SQL Result: {test_live_model('Find the names of all students who live in the dorms.')}")