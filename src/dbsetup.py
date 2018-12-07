import sqlite3

db = sqlite3.connect("//h023filesrv01/OldPupilSHare/New folder/thumbs.db")

cursor = db.cursor()

try:
    cursor.execute("""
        DROP TABLE messages
    """)
    cursor.execute("""
        DROP TABLE users
    """)
except:
    pass

cursor.execute("""
    CREATE TABLE messages(id INTEGER PRIMARY KEY, time TEXT, name TEXT, message TEXT, prefix INTEGER, colour TEXT)
""")

cursor.execute("""
    CREATE TABLE users(id INTEGER PRIMARY KEY, nickname TEXT, status INTEGER)
""")

db.commit()


db.close()
