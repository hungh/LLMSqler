from faker import Faker
from psycopg2.extras import execute_values
from global_config import DB_NAME, DB_USER, DB_PORT
import argparse
import psycopg2

from introspect_schema import get_tables_from_schema



# List of tables to populate
# ['organizations', 'customers', 'users', 'user_roles', 'roles', 'role_permissions', 'permissions', 
# 'subscriptions', 'plans', 'invoices', 'payments', 'usage_events', 'organization_feature_flags', 
# 'feature_flags', 'support_tickets', 'audit_logs']

fake = Faker()

def generate_value(col_name, data_type):
    """
    Generate a fake value for a given column name and data type.
    email, name, address, created_at & updated_at are populated with fake data.
    Args:
        col_name (str): The name of the column.
        data_type (str): The data type of the column.
    
    Returns:
        The generated fake value.
    """
    col = col_name.lower()
    if "email" in col:
        return fake.email()
    if "name" in col and "company" in col:
        return fake.company()
    if "name" in col:
        return fake.name()
    if "address" in col:
        return fake.address()
    if "created_at" in col or "updated_at" in col:
        return fake.date_time_between(start_date="-2y", end_date="now")
    if data_type.startswith("int"):
        return fake.random_int(min=0, max=10000)
    if data_type.startswith("numeric") or data_type.startswith("decimal"):
        return round(fake.pyfloat(left_digits=4, right_digits=2, positive=True), 2)
    # fallback
    return fake.text(max_nb_chars=80)


def populate_table(conn, table, n_rows=1000):
    """
    Populate a table with fake data.
    
    Args:
        conn: The database connection.
        table (str): The name of the table to populate.
        n_rows (int): The number of rows to insert.
    """
    cur = conn.cursor()
    cur.execute(f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position;
    """, (table,))
    cols = cur.fetchall()
    col_names = [c[0] for c in cols]

    rows = []
    for _ in range(n_rows):
        row = [generate_value(name, dtype) for name, dtype in cols]
        rows.append(row)

    execute_values(
        cur,
        f"INSERT INTO {table} ({', '.join(col_names)}) VALUES %s",
        rows
    )
    conn.commit()

# main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # required server and password
    parser.add_argument("--password", required=True, help="password")
    parser.add_argument("--server", required=True, help="server")
    args = parser.parse_args()
    
    conn = psycopg2.connect("host=" + args.server + " port=" + str(DB_PORT) + " dbname=" + DB_NAME + " user=" + DB_USER + " password=" + args.password)

    tables = get_tables_from_schema(conn)
    for t in tables:
        populate_table(conn, t, n_rows=5000)
    conn.close()