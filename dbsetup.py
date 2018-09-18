import sqlite3

# "//H023FILESRV01/OldPupilSHare/slamjam/messenger/defaultserver.db")

db = sqlite3.connect("//h023filesrv01/OldPupilSHare/gamersquad/wpservers/general.db")

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
