import sqlite3

conn = sqlite3.connect("chroma/chroma.sqlite3")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM embeddings;")
rows = cursor.fetchall()

for row in rows:
    print(row)
