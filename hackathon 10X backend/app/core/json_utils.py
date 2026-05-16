import json
import re
import logging

import numpy as pd_np # Using a safe import alias

logger = logging.getLogger(__name__)

MOJIBAKE_REPLACEMENTS = {
    "â": "-",
    "â€”": "-",
    "â": "-",
    "â€“": "-",
    "â": "'",
    "â€™": "'",
    "â": "'",
    "â€˜": "'",
    "â": '"',
    "â€œ": '"',
    "â": '"',
    "â€": '"',
    "â¢": "-",
    "â€¢": "-",
    "â¥": ">=",
    "â‰¥": ">=",
    "â¤": "<=",
    "â‰¤": "<=",
    "Ã": "x",
}

class NumpyEncoder(json.JSONEncoder):
    """ Custom encoder for numpy data types """
    def default(self, obj):
        if isinstance(obj, (pd_np.int_, pd_np.intc, pd_np.intp, pd_np.int8,
                            pd_np.int16, pd_np.int32, pd_np.int64, pd_np.uint8,
                            pd_np.uint16, pd_np.uint32, pd_np.uint64)):
            return int(obj)
        elif isinstance(obj, (pd_np.float_, pd_np.float16, pd_np.float32, pd_np.float64)):
            return float(obj)
        elif isinstance(obj, (pd_np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def clean_text_encoding(value):
    if isinstance(value, str):
        if "â" in value or "Ã" in value:
            try:
                value = value.encode("latin1").decode("utf-8")
            except UnicodeError:
                pass
        for bad, good in MOJIBAKE_REPLACEMENTS.items():
            value = value.replace(bad, good)
        return value
    if isinstance(value, list):
        return [clean_text_encoding(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_text_encoding(item) for key, item in value.items()}
    return value

def extract_json_from_text(text: str) -> dict:
    """
    Attempts to extract and parse a JSON object from a string that might
    contain markdown blocks or other text.
    """
    try:
        return clean_text_encoding(json.loads(text))
    except json.JSONDecodeError:
        pass
        
    # Try to find a JSON block using regex
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        try:
            return clean_text_encoding(json.loads(json_match.group(1)))
        except json.JSONDecodeError:
            pass
            
    # Try to find anything between { and }
    json_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if json_match:
        try:
            return clean_text_encoding(json.loads(json_match.group(1)))
        except json.JSONDecodeError:
            pass
            
    logger.error(f"Failed to extract JSON from text: {text}")
    raise ValueError("Could not parse JSON from LLM response.")
