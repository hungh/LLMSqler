from datasets import load_dataset

from trl import SFTTrainer, SFTConfig
from transformers import DataCollatorForLanguageModeling

from qwen_ft import tokenizer, model
from spider_ds import format_dataset

# the execution path is from the root of the project
DATA_PATH = ".model"

# Load the raw dataset
raw_dataset = load_dataset("xlangai/spider", split="train")

# Split: 90% Train, 10% Validation
split_dataset = raw_dataset.train_test_split(test_size=0.1, seed=42)

# Apply the tokenizer
# remove_columns is vital to prevent the Trainer from passing non-tensors to the model
# Format into 'prompt' and 'completion' columns
train_dataset = split_dataset["train"].map(format_dataset, remove_columns=raw_dataset.column_names)
eval_dataset = split_dataset["test"].map(format_dataset, remove_columns=raw_dataset.column_names)


sft_config = SFTConfig(
    output_dir=f"{DATA_PATH}/llmsqler_v1",
    max_length=2048,
    dataset_text_field=None,        # Ignored when using prompt/completion
    packing=False,                  # Mandatory for completion_only_loss
    completion_only_loss=True,      # THE KEY: Masks 'prompt' in labels automatically
    
    # Hardware Optimizations
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    optim="paged_adamw_32bit",      # Use your 32GB CPU RAM
    bf16=True,
    gradient_checkpointing=True,
    
    # Training Loop
    max_steps=300, # 500 
    save_steps=100,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=100,
    save_total_limit=3,
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    # no confusion by padding on the right side
    tokenizer.padding_side = "right"

# Initialize the Trainer as supervised fine tuning
# Trainer Config
trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    args=sft_config,
    # Standard collator is fine because completion_only_loss=True 
    # handles the label masking inside the SFTTrainer.
    # data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Start Fine-tuning
trainer.train()

# Final Save
trainer.model.save_pretrained(f"{DATA_PATH}/llmsqler-final")