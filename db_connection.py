# utils/db_connection.py
import mysql.connector
import pandas as pd

# --- Hardcoded DB config ---
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "cric_analytics_db",
}

def get_db_connection():
    """Return a live MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)

def run_query(sql: str) -> pd.DataFrame:
    """Run SQL and return DataFrame."""
    conn = get_db_connection()
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()
