import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

create_table_query = "CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)"
conn.execute(create_table_query)
print("Created table successfully!")

conn.commit()
def user_exists(username):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT username FROM users WHERE username = ?', (username,))
    result = cur.fetchone()
    con.close()
    return result is not None

conn.close()
print("Records deleted successfully!")