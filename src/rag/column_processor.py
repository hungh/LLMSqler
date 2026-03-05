from .global_config import SQL_KEYWORDS, DANGEROUS_CHARS, MAX_LENGTHS
import logging
from faker import Faker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()
class ColumnProcessor:
    """Centralized column processing with security rules."""
       
    @classmethod
    def get_column_category(cls, column_name: str, data_type: str) -> str:
        """Categorize column for appropriate processing."""
        name_lower = column_name.lower()
        
        if 'email' in name_lower:
            return 'email'
        elif 'id' in name_lower and 'uuid' in data_type.lower():
            return 'uuid'
        elif 'name' in name_lower:
            return 'name'
        elif any(time_field in name_lower for time_field in ['created_at', 'updated_at', 'timestamp']):
            return 'timestamp'
        elif any(num_field in name_lower for num_field in ['amount', 'price', 'cost', 'quantity']):
            return 'numeric'
        elif any(text_field in name_lower for text_field in ['description', 'content', 'notes']):
            return 'text'
        else:
            return 'general'
    
    @classmethod
    def sanitize_value(cls, value: str, column_category: str) -> str:
        """Sanitize value based on security rules."""
        if value is None:
            return ""
        
        str_value = str(value).strip()
        
        # Remove dangerous characters
        for char in cls.DANGEROUS_CHARS:
            str_value = str_value.replace(char, '')
        
        # Check for SQL keywords
        words = str_value.upper().split()
        for word in words:
            if word in cls.SQL_KEYWORDS:
                logger.warning(f"Detected potential SQL injection: {word}")
                return ""
        
        # Apply length limits
        max_len = cls.MAX_LENGTHS.get(column_category, cls.MAX_LENGTHS['default'])
        if len(str_value) > max_len:
            str_value = str_value[:max_len]
        
        return str_value
    
    @classmethod
    def generate_faker_value(cls, column_category: str) -> str:
        """Generate faker value based on column category."""
        if column_category == 'email':
            return fake.email()
        elif column_category == 'uuid':
            return fake.uuid4()
        elif column_category == 'name':
            return fake.name()
        elif column_category == 'timestamp':
            return fake.date_time_between(start_date="-2y", end_date="now").isoformat()
        elif column_category == 'numeric':
            return str(fake.pyfloat(left_digits=4, right_digits=2, positive=True))
        elif column_category == 'text':
            return fake.text(max_nb_chars=200)
        else:
            return fake.text(max_nb_chars=50)
