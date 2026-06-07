import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.execute("CREATE TABLE users (id INTEGER, data TEXT)")
cursor.execute("INSERT INTO users VALUES (1, 'Admin Data')")
cursor.execute("INSERT INTO users VALUES (2, 'Secret User')")

user_input = input()

query = "SELECT * FROM users WHERE id='" + user_input + "'"
cursor.execute(query)

print(cursor.fetchall())
