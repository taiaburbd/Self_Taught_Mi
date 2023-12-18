import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('ALTER TABLE questions ADD COLUMN image_path VARCHAR(255)')

conn.close()


print("Done!!!")