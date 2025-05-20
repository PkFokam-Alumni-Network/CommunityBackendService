import sqlite3
import psycopg2
import os
from getpass import getpass

def migrate_sqlite_to_postgres():
    # SQLite connection
    print("Connecting to SQLite database...")
    sqlite_con = sqlite3.connect("database.db")
    sqlite_cur = sqlite_con.cursor()
    
    # Get PostgreSQL connection details
    pg_host = input("Enter PostgreSQL host (default: localhost): ") or "localhost"
    pg_port = input("Enter PostgreSQL port (default: 5432): ") or "5432"
    pg_user = input("Enter PostgreSQL username (default: postgres): ") or "postgres"
    pg_pass = input("Enter PostgreSQL password: ")
    pg_db = input("Enter PostgreSQL database name (default: pkfalumni): ") or "pkfalumni"
    
    # PostgreSQL connection
    print(f"Connecting to PostgreSQL database {pg_db}...")
    pg_con = psycopg2.connect(
        host=pg_host,
        port=pg_port,
        user=pg_user,
        password=pg_pass,
        dbname=pg_db
    )
    pg_cur = pg_con.cursor()
    
    # Get all tables from SQLite
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = sqlite_cur.fetchall()
    
    # For each table
    for table_row in tables:
        table_name = table_row[0]
        print(f"Processing table: {table_name}")
        
        # Get table schema
        sqlite_cur.execute(f"PRAGMA table_info({table_name});")
        columns = sqlite_cur.fetchall()
        
        # Create table in PostgreSQL with correct type mapping
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        column_defs = []
        
        # Special handling for user_events table which has composite primary key
        if table_name == "user_events":
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_events (
                user_email TEXT,
                event_id INTEGER,
                PRIMARY KEY (user_email, event_id)
            );
            """
        else:
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                
                # Map SQLite types to PostgreSQL types with special handling for boolean
                if col_type.upper() == "BOOLEAN" or col_name == "is_active":
                    pg_type = "BOOLEAN"
                else:
                    pg_type = {
                        "INTEGER": "INTEGER",
                        "TEXT": "TEXT",
                        "REAL": "DOUBLE PRECISION",
                        "BLOB": "BYTEA",
                        "BOOLEAN": "BOOLEAN",
                        "DATETIME": "TIMESTAMP"
                    }.get(col_type.upper(), "TEXT")
                
                col_def = f"{col_name} {pg_type}"
                
                if is_pk:
                    if pg_type == "INTEGER":
                        col_def += " PRIMARY KEY"
                    else:
                        col_def += " PRIMARY KEY"
                
                if not_null:
                    col_def += " NOT NULL"
                    
                column_defs.append(col_def)
            
            create_table_sql += ",\n".join(column_defs)
            create_table_sql += "\n);"
        
        # Create the table in PostgreSQL
        try:
            pg_cur.execute("DROP TABLE IF EXISTS " + table_name + " CASCADE;")
            pg_cur.execute(create_table_sql)
            pg_con.commit()
            print(f"  Created table: {table_name}")
        except Exception as e:
            pg_con.rollback()
            print(f"  Error creating table {table_name}: {e}")
            continue
        
        # Get data from SQLite
        sqlite_cur.execute(f"SELECT * FROM {table_name};")
        rows = sqlite_cur.fetchall()
        
        if not rows:
            print(f"  No data in table: {table_name}")
            continue
        
        # Get column names
        column_names = [col[1] for col in columns]
        
        # Insert data into PostgreSQL
        placeholders = ", ".join(["%s"] * len(column_names))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders});"
        
        try:
            for row in rows:
                # Convert data types as needed
                converted_row = []
                for i, val in enumerate(row):
                    col_name = column_names[i]
                    # Convert SQLite integers (0/1) to PostgreSQL booleans for boolean columns
                    if col_name == "is_active" and val is not None:
                        converted_row.append(val == 1)
                    else:
                        converted_row.append(val)
                
                try:
                    pg_cur.execute(insert_sql, converted_row)
                except Exception as e:
                    print(f"  Error inserting row: {e}")
                    pg_con.rollback()
                    continue
            
            pg_con.commit()
            print(f"  Inserted {len(rows)} rows into {table_name}")
        except Exception as e:
            pg_con.rollback()
            print(f"  Error inserting data into {table_name}: {e}")
    
    # Close connections
    sqlite_con.close()
    pg_con.close()
    
    print("Migration completed!")

if __name__ == "__main__":
    # Ensure psycopg2 is installed
    try:
        import psycopg2
    except ImportError:
        print("psycopg2 is not installed. Installing...")
        os.system("pip install psycopg2-binary")
    
    migrate_sqlite_to_postgres()