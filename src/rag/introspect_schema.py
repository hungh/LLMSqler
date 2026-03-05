
# Usage example: python scripts/introspect_schema.py --password your_password
# Returns a list of table names in the public schema
# ['organizations', 'customers', 'users', 'user_roles', 'roles', 'role_permissions', 'permissions', 
# 'subscriptions', 'plans', 'invoices', 'payments', 'usage_events', 'organization_feature_flags', 
# 'feature_flags', 'support_tickets', 'audit_logs']

def get_tables_from_schema(db_connection):
    """
    Get all table names from the public schema of a PostgreSQL database.
    
    Args:
        db_connection: The database connection object
    
    Returns:
        list: A list of table names in the public schema
    """
    cur = db_connection.cursor()

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)
    tables = [r[0] for r in cur.fetchall()]
    # print(tables)
    cur.close()
    return tables