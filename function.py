import psycopg2
import os

def get_connection():
    
    conn = psycopg2.connect(
        database=os.environ["POSTGRES_DB"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"]        
    )
    return conn

def select_DB(what, table, join, condition):
    conn = get_connection()
    cursor =conn.cursor()

    select = f"""
                SELECT {what} FROM {table} {join} {condition};
            """
    cursor.execute(select)
    name = cursor.fetchall()
    conn.close()

    return name

def insert_DB(table, what, data):
    conn = get_connection()
    cursor =conn.cursor()

    insert = f"""
                INSERT INTO {table} ({what})
                VALUES {data}
            """
    cursor.execute()
    conn.commit()
    conn.close()

    return insert