
import re
import json

def extract_json(text: str):
    """
    Extract JSON from a string that may contain code fences or other text.
    
    Args:
        text: String that may contain JSON
        
    Returns:
        Parsed JSON object or list
    """
    # Remove code fences anywhere
    text = re.sub(r"```json|```", "", text, flags=re.I).strip()

    # Find all JSON-like objects
    objects = re.findall(r"\{[^{}]*\}", text, flags=re.S)

    if not objects:
        raise ValueError("No JSON objects found")

    # If multiple objects, wrap them into a list
    if len(objects) > 1:
        json_str = "[" + ",".join(objects) + "]"
    else:
        json_str = objects[0]

    return json.loads(json_str)
