1. Prompt LLMs to generate schema
    example prompt: 

```markdown
You are a senior data architect.
Design a realistic relational schema for a mid‑size B2B SaaS company that sells subscriptions to enterprise customers.
Requirements:
• 	12–20 tables
• 	Include customers, users, subscriptions, invoices, payments, usage_events, audit_logs, feature_flags, support_tickets, organizations, roles, permissions
• 	Use PostgreSQL dialect
• 	Define primary keys, foreign keys, indexes, and reasonable data types
• 	Include some nullable fields and some NOT NULL
• 	Output only SQL DDL in a single code block.

```
2. Install Postgres and operate it (Ubuntu)

sudo apt install -y postgresql 

connect to postgresql
```bash
psql -U postgres -h localhost -p 5432 ( or run sudo -u postgres psql to run as admin)


# if you have a database
psql -U postgres -h localhost -p 5432 -d rag_llmsqler

# to stop/restart postgresql
sudo systemctl stop [start] postgresql
```
3. Create database 
```bash
CREATE DATABASE rag_llmsqler;

ALTER ROLE hung CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE rag_llmsqler TO hung;
GRANT ALL ON SCHEMA public TO hung;
ALTER SCHEMA public OWNER TO hung;
GRANT CREATE ON SCHEMA public TO hung;

then exit \q to terminal

psql rag_llmsqler -f llm_gen_schemas.sql

where hung: is the username
```

4. Validate if the schema is created
```bash
psql rag_llmsqler -c "\dt"
```

```markdown
   List of relations
 Schema |            Name            | Type  | Owner
--------+----------------------------+-------+-------
 public | audit_logs                 | table | hung
 public | customers                  | table | hung
 public | feature_flags              | table | hung
 public | invoices                   | table | hung
 public | organization_feature_flags | table | hung
 public | organizations              | table | hung
 public | payments                   | table | hung
 public | permissions                | table | hung
 public | plans                      | table | hung
 public | role_permissions           | table | hung
 public | roles                      | table | hung
 public | subscriptions              | table | hung
 public | support_tickets            | table | hung
 public | usage_events               | table | hung
 public | user_roles                 | table | hung
 public | users                      | table | hung
(16 rows)
```
5. Ensure the database is accessible
On the postgresql server, edit the postgresql.conf file
```bash
sudo vi /etc/postgresql/16/main/postgresql.conf
```
Update the following line:
```
listen_addresses = '*'
```
(or specific IP address if needed)
restart postgresql service
```bash
sudo systemctl restart postgresql
```
6. Open postgresql internal security lock for local network
go to the pg_hba.conf file
```bash
sudo vi /etc/postgresql/16/main/pg_hba.conf
```
add the following line:
```bash
host    all             all             192.168.1.0/24          scram-sha-256
```
restart postgresql service
```bash
sudo systemctl restart postgresql
```
If you run postgresql on Ubuntu server, make sure to allow the firewall to access the database
```bash
sudo ufw allow 5432
```
IMPORTANT: in a production "Distributed Systems" environment, Check the Security Groups (AWS) or Ingress Controllers (K8s) first before doing the above steps.

7. Export all public schamas to a file
```bash
psql -d rag_llmsqler -t -A -F"," -c "
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
" > columns.csv

```
returns something like this 

```markdown
audit_logs,entity_type,character varying
audit_logs,entity_id,uuid
audit_logs,old_values,jsonb
audit_logs,new_values,jsonb
audit_logs,ip_address,inet
audit_logs,created_at,timestamp with time zone
customers,id,uuid
customers,organization_id,uuid
customers,external_crm_id,character varying
customers,account_manager,character varying
customers,contract_start_date,date
customers,contract_end_date,date
customers,status,character varying
customers,created_at,timestamp with time zone
feature_flags,id,uuid
feature_flags,key,character varying
feature_flags,description,text
feature_flags,is_enabled,boolean
feature_flags,rollout_percentage,integer
```
