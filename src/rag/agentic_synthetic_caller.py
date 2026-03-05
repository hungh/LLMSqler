
import logging
from typing import List, Dict, Tuple, Set
import psycopg2
from psycopg2.extras import execute_values
from .global_config import DB_NAME, DB_USER, DB_PORT
from .column_processor import ColumnProcessor
from .qwen_data_generator import LocalQwenGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Optimized synthetic data generator using local Qwen model."""
    
    def __init__(self):
        """Initialize with local Qwen model."""
        self.qwen_generator = LocalQwenGenerator()
        self.processor = ColumnProcessor()
    
    def generate_row(self, table_name: str, columns: List[Dict[str, str]]) -> Tuple:
        """Generate a single row of data."""
        row_data = {}
        llm_columns = []
        
        # Categorize columns
        for col in columns:
            category = self.processor.get_column_category(col['name'], col['type'])
            
            if category in ['email', 'uuid', 'name', 'timestamp', 'numeric']:
                # Use faker for standard types
                row_data[col['name']] = self.processor.generate_faker_value(category)
            else:
                # Use LLM for complex/unknown types
                llm_columns.append(col)
        
        # Generate LLM data if needed
        if llm_columns:
            try:
                llm_data = self.qwen_generator.generate_structured_data(table_name, llm_columns)
                
                # Validate and sanitize LLM data
                for col in llm_columns:
                    category = self.processor.get_column_category(col['name'], col['type'])
                    if col['name'] in llm_data:
                        row_data[col['name']] = self.processor.sanitize_value(
                            llm_data[col['name']], category
                        )
                    else:
                        row_data[col['name']] = self.processor.generate_faker_value(category)
                        
            except Exception as e:
                logger.error(f"LLM generation failed for {table_name}: {e}")
                # Fallback to faker
                for col in llm_columns:
                    category = self.processor.get_column_category(col['name'], col['type'])
                    row_data[col['name']] = self.processor.generate_faker_value(category)
        
        # Ensure all columns are present
        column_names = [col['name'] for col in columns]
        for col_name in column_names:
            if col_name not in row_data:
                category = self.processor.get_column_category(col_name, 'text')
                row_data[col_name] = self.processor.generate_faker_value(category)
        
        # Return in correct order
        return tuple(row_data[col_name] for col_name in column_names)
    
    def populate_table(self, conn, table_name: str, n_rows: int = 1000):
        """Populate table with synthetic data."""
        logger.info(f"Populating {table_name} with {n_rows} rows...")
        
        cur = conn.cursor()
        
        # Get schema
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = [{'name': row[0], 'type': row[1]} for row in cur.fetchall()]
        col_names = [col['name'] for col in columns]
        
        # Batch processing
        batch_size = 50  # Smaller batches for LLM processing
        for i in range(0, n_rows, batch_size):
            batch_rows = []
            
            for j in range(min(batch_size, n_rows - i)):
                try:
                    row = self.generate_row(table_name, columns)
                    batch_rows.append(row)
                except Exception as e:
                    logger.error(f"Error generating row {i+j}: {e}")
                    continue
            
            # Insert batch
            if batch_rows:
                try:
                    execute_values(
                        cur,
                        f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES %s",
                        batch_rows
                    )
                    conn.commit()
                    logger.info(f"Inserted {len(batch_rows)} rows into {table_name}")
                except Exception as e:
                    logger.error(f"Database error: {e}")
                    conn.rollback()
        
        cur.close()

# Usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True, help="Database server")
    parser.add_argument("--password", required=True, help="Database password")
    parser.add_argument("--table", help="Specific table to populate")
    parser.add_argument("--rows", type=int, default=1000, help="Rows per table")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = SyntheticDataGenerator()
    
    # Connect and populate
    conn = psycopg2.connect(
        host=args.server,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=args.password
    )
    
    try:
        if args.table:
            generator.populate_table(conn, args.table, args.rows)
        else:
            from .introspect_schema import get_tables_from_schema
            tables = get_tables_from_schema(conn)
            for table in tables:
                generator.populate_table(conn, table, args.rows)
    finally:
        conn.close()