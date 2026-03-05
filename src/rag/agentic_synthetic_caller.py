
import logging
from typing import List, Dict, Tuple
import psycopg2
from psycopg2.extras import execute_values
from .global_config import DB_NAME, DB_USER, DB_PORT, LOAD_SCHEMA_QUERY
from .column_processor import ColumnProcessor
from .qwen_data_generator import LocalQwenGenerator
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Optimized synthetic data generator using local Qwen model."""
    
    def __init__(self):
        """Initialize with local Qwen model."""
        self.qwen_generator = LocalQwenGenerator()
        self.processor = ColumnProcessor()
    
    def generate_row(self, table_name: str, columns: List[Dict[str, str]], is_dry_run: bool = False) -> Tuple:
        """Generate a single row of data."""
        row_data = {}
        llm_columns = []

        logger.debug(f"Generating row for table: {table_name}" + " " * 50)
        
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
                llm_data = self.qwen_generator.generate_structured_data(table_name, llm_columns, is_dry_run)
                start_time = time.time()
                end_time = time.time()
                logger.debug(f"LLM generation took {end_time - start_time:.2f} seconds for {table_name}")
                
                # Validate and sanitize LLM data
                logger.debug(f"LLM data for {table_name}: {llm_data}" + " " * 50)
                logger.debug(f"LLM columns: {llm_columns}" + " " * 50)
                for col in llm_columns:
                    category = self.processor.get_column_category(col['name'], col['type'])
                    # ensure the column name is in the agent's response JSON (security check)
                    if col['name'] in llm_data:
                        row_data[col['name']] = self.processor.sanitize_value(
                            llm_data[col['name']], category
                        )
                        logger.debug(f"LLM Generated value for {col['name']}: {row_data[col['name']]}")
                    else:
                        row_data[col['name']] = self.processor.generate_faker_value(category)
                        logger.warning(f"LLM did not return value for {col['name']}, using faker: {row_data[col['name']]}")
                        
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
    
    def populate_table(self, conn, table_name: str, n_rows: int = 1000, is_dry_run: bool = False):
        """Populate table with synthetic data."""
        logger.debug(f"Populating {table_name} with {n_rows} rows...")
        
        cur = conn.cursor()

        logger.debug(f"Fetching schema for {table_name}...")
        # Get schema with key type and reference table information
        cur.execute(LOAD_SCHEMA_QUERY, (table_name, table_name, table_name))

        columns = [{'name': row[0], 'type': row[1], 'key_type': row[2], 'reference_table': row[3] if row[3] else None} for row in cur.fetchall()]
        
        col_names = [col['name'] for col in columns]
        
        # Batch processing
        batch_size = max(1, n_rows // 7)  # Smaller batches for LLM processing
        for i in range(0, n_rows, batch_size):
            batch_rows = []

            # batch_size or the remaining n_rows - i 
            for j in range(min(batch_size, n_rows - i)):
                try:
                    row = self.generate_row(table_name, columns, is_dry_run)
                    batch_rows.append(row)
                except Exception as e:
                    logger.error(f"Error generating row {i+j}: {e}")
                    continue
            
            # Insert batch
            if batch_rows:
                try:
                    if is_dry_run:
                        logger.warning(f"[DRY RUN] Would insert {len(batch_rows)} rows into {table_name}")
                        logger.debug(f"Sample row: {batch_rows[0]}")
                    else:
                        execute_values(
                            cur,
                            f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES %s",
                            batch_rows
                        )
                        logger.debug(f"Inserted {len(batch_rows)} rows into {table_name}")
                        conn.commit()
                        # cache the inserted rows to Redis server (table_name, list_ids)
                        logger.debug(f"Committed {len(batch_rows)} rows into {table_name}")
                    logger.debug(f"Inserted {len(batch_rows)} rows into {table_name}")
                except Exception as e:
                    logger.error(f"Database error: {e}")
                    if not is_dry_run:
                        conn.rollback()
        
        cur.close()

# Usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True, help="Database server")
    parser.add_argument("--password", required=True, help="Database password")
    parser.add_argument("--table", help="Specific table to populate")
    parser.add_argument("--rows", type=int, default=49, help="Rows per table")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
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
    
    print(f"args.dry_run: {args.dry_run}")
    try:
        if args.table:
            generator.populate_table(conn, args.table, args.rows, args.dry_run)
        else:
            from .introspect_schema import get_tables_from_schema
            tables = get_tables_from_schema(conn)
            logger.debug(f"Found {len(tables)} tables with {', '.join(tables)}")
            for table in tables:
                logger.debug(f">>>>>>>>> Populating table {table}")
                generator.populate_table(conn, table, args.rows, args.dry_run)
                logger.debug(f"<<<<<<<<< Finished populating table {table}")
    finally:
        conn.close()