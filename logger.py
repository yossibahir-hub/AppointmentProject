import sqlite3
import datetime

def log_sql(query: str, params: tuple = ()):
    """Logs SQL queries with timestamps to log.txt."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] SQL: {query} | Params: {params}\n"
    
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

def execute_and_log(cursor, query: str, params: tuple = ()):
    """Executes a SQL query and automatically logs it."""
    log_sql(query, params)
    return cursor.execute(query, params)