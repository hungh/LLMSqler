# Database configuration
DB_NAME = "rag_llmsqler"
DB_USER = "postgres"
DB_PORT = 5432

# Caching Layer Redis configuration
REDIS_HOST = "hung-gig1.local"
REDIS_PORT = 6379
REDIS_DB = 0    

# Security configurations
SQL_KEYWORDS = {'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'EXEC', 'UNION', 'SELECT'}
DANGEROUS_CHARS = {'<', '>', '&', '"', "'", ';', '--', '/*', '*/'}
MAX_LENGTHS = {
    'email': 255,
    'name': 100,
    'id': 36,  # UUID length
    'default': 1000
    }

# POSTGRESQL QUERIES
LOAD_SCHEMA_QUERY = """
            SELECT 
                c.column_name, 
                c.data_type,
                CASE 
                    WHEN pk.column_name IS NOT NULL THEN 1  -- Primary key
                    WHEN fk.column_name IS NOT NULL THEN 2  -- Foreign key
                    ELSE 0                                 -- Not a key
                END as key_type,
                fk.reference_table
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT ku.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage ku ON tc.constraint_name = ku.constraint_name
                WHERE tc.table_schema = 'public' 
                    AND tc.table_name = %s
                    AND tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.column_name = pk.column_name
            LEFT JOIN (
                SELECT 
                    ku.column_name,
                    ccu.table_name as reference_table,
                    tc.constraint_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage ku ON tc.constraint_name = ku.constraint_name
                JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_schema = 'public' 
                    AND tc.table_name = %s
                    AND tc.constraint_type = 'FOREIGN KEY'
            ) fk ON c.column_name = fk.column_name
            WHERE c.table_schema = 'public' AND c.table_name = %s
            ORDER BY c.ordinal_position;
        """