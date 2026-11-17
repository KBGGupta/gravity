import sqlite3
import os

def sqlite_list_tables(base_dir: str, db_path: str) -> str:
    full_path = os.path.normpath(os.path.join(base_dir, db_path)) if not os.path.isabs(db_path) else db_path
    if not os.path.exists(full_path):
        return f"Error: Database file '{full_path}' does not exist."

    try:
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return "Tables:\n" + "\n".join(f"- {t}" for t in tables) if tables else "No user tables found in database."
    except Exception as e:
        return f"Database Error: {str(e)}"

def sqlite_describe_table(base_dir: str, db_path: str, table_name: str) -> str:
    full_path = os.path.normpath(os.path.join(base_dir, db_path)) if not os.path.isabs(db_path) else db_path
    if not os.path.exists(full_path):
        return f"Error: Database file '{full_path}' does not exist."

    try:
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols = cursor.fetchall()
        conn.close()
        if not cols:
            return f"Table '{table_name}' does not exist or has no columns."
        
        info = [f"Table: {table_name}"]
        for c in cols:
            # c: (cid, name, type, notnull, dflt_value, pk)
            pk = " [PRIMARY KEY]" if c[5] else ""
            notnull = " NOT NULL" if c[3] else ""
            info.append(f"  - {c[1]} ({c[2]}){pk}{notnull}")
        return "\n".join(info)
    except Exception as e:
        return f"Database Error: {str(e)}"

def sqlite_query(base_dir: str, db_path: str, query: str) -> str:
    full_path = os.path.normpath(os.path.join(base_dir, db_path)) if not os.path.isabs(db_path) else db_path
    parent_dir = os.path.dirname(full_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    try:
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        cursor.execute(query)

        # Check if it was a SELECT query
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(100) # limit to 100 rows for readability
            conn.close()

            # Format into clean table
            col_str = " | ".join(columns)
            sep = "-" * len(col_str)
            row_strs = [" | ".join(str(val) for val in row) for row in rows]
            return f"Query Result ({len(rows)} rows):\n{col_str}\n{sep}\n" + "\n".join(row_strs)
        else:
            conn.commit()
            changes = conn.total_changes
            conn.close()
            return f"Query executed successfully. Rows affected: {changes}"
    except Exception as e:
        return f"Database Error: {str(e)}"
