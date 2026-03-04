import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# QLoRA configuration for 4-bit quantization (NF4 = Normal Float 4-bit for storage and BF16 for computation)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model_id = "Qwen/Qwen2.5-1.5B-Instruct"  # "Qwen/Qwen2.5-3B-Instruct"

# load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)

# load model with QLoRA
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# to save vram, we enable Gradient Checkpointing
model.gradient_checkpointing_enable()

# prepare for 4-bit training
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,  # LoRA rank (for A and B matrices in LoRA)
    lora_alpha=32,  # Scaling factor for LoRA updates, alpha/r should be around 2
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",  
)


model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

print("Model loaded successfully! and it uses ", model.device)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
model = model.to(device)

__all__ = ['tokenizer', 'model', 'lora_config']