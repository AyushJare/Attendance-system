import psycopg2
from psycopg2 import sql

# Connect to default postgres database
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="Eagle_Shadow69",  # ← UPDATED
    database="postgres"
)

# Set autocommit mode (required for DROP DATABASE)
conn.autocommit = True
cursor = conn.cursor()

try:
    # Drop existing database
    cursor.execute("DROP DATABASE IF EXISTS attendance_db;")
    print("✅ Database dropped")
    
    # Create new database
    cursor.execute("CREATE DATABASE attendance_db;")
    print("✅ Database created")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    cursor.close()
    conn.close()