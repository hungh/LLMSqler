import psycopg2

def generate_large_schema(num_departments=50):
    conn = psycopg2.connect("host=localhost dbname=dev_db user=postgres password=pass")
    cur = conn.cursor()
    
    for i in range(num_departments):
        dept_name = f"dept_{i}"
        # Create a set of 5-10 tables per department
        cur.execute(f"CREATE TABLE {dept_name}_employees (id SERIAL PRIMARY KEY, name TEXT, role_id INT);")
        cur.execute(f"CREATE TABLE {dept_name}_projects (id SERIAL PRIMARY KEY, title TEXT, budget NUMERIC);")
        cur.execute(f"CREATE TABLE {dept_name}_assets (id SERIAL PRIMARY KEY, asset_name TEXT, value NUMERIC);")
        # Add random columns to create "noise" for the LLM
        cur.execute(f"ALTER TABLE {dept_name}_employees ADD COLUMN metadata_jsonb_{i} JSONB;")
        
    conn.commit()
    print(f"Generated {num_departments * 3} tables.")

# generate_large_schema(100) # This will create 300 tables