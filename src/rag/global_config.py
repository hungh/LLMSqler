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