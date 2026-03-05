from ..pretraining.qwen import model_and_tokenizer
from typing import List, Dict
import torch
import json
import logging
from .common_utils import extract_json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalQwenGenerator:
    """Local Qwen model for synthetic data generation."""
    
    def __init__(self):
        """Initialize local Qwen model."""
        model, tokenizer = model_and_tokenizer()
        self.tokenizer = tokenizer
        self.model = model
        
    def generate_structured_data(self, table_name: str, columns: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Generate structured data using local Qwen model.
        
        Args:
            table_name: Name of the table
            columns: List of column dictionaries with column 'name' and its 'type' keys
            
        Returns:
            Dictionary with column names as keys and generated values as values
        """
        # Create prompt for structured output
        column_info = "\n".join([f"- {col['name']} ({col['type']})" for col in columns])
        
        # Format with Qwen chat template manually
        prompt = f"""<|im_start|>system
        You are a helpful assistant that generates realistic data in JSON format.<|im_end|>
        <|im_start|>user
        Generate realistic data for table '{table_name}' with these columns:
        {column_info}

        Requirements:
        - Return ONLY valid JSON
        - Ensure data consistency
        - Keep values concise and appropriate
        - No SQL or code content

        JSON format:
        {{"""

        # Add column placeholders
        for col in columns:
            prompt += f"\n  \"{col['name']}\": \"value_here\","

        prompt = prompt.rstrip(',') + f"\n}}<|im_end|>\n<|im_start|>assistant\n"

        print(prompt)       
        try:
           
           
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.model.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=300,
                    # temperature=0.7,
                    do_sample=False,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
          
          
            # Extract generated text
            generated_text = self.tokenizer.decode(
                outputs[0][len(inputs["input_ids"][0]):], 
                skip_special_tokens=True
            ).strip()
            
            print(f"generated_text: {generated_text}")
           
            # Clean and parse JSON
            result = extract_json(generated_text)
            if result:
                return result
            else:
                logger.error("No valid JSON found in generated text")
                return {}
                
        except Exception as e:
            logger.error(f"Error generating data with local Qwen: {e}")
            return {}


# test the generator to run 'python -m src.rag.qwen_data_generator'
if __name__ == "__main__":
    generator = LocalQwenGenerator()
    table_name = "users"
    columns = [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "age", "type": "int"}
    ]
    data = generator.generate_structured_data(table_name, columns)
    print(data)
