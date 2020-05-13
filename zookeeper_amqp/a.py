import sqlite3

db_connection = sqlite3.connect('database.db',check_same_thread=False)
db_cursor = db_connection.cursor()


db_cursor.execute("CREATE TABLE IF NOT EXISTS users (username varchar,password varchar)")

db_cursor.execute("CREATE TABLE IF NOT EXISTS user_ride(ride INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,timestamp TEXT,source TEXT,destination TEXT,ride_mate TEXT)")

db_connection.commit()
'''
db_cursor.execute("INSERT INTO users values('u1','p1')")
db_cursor.execute("INSERT INTO users values('u2','p2')")

db_connection.commit()
'''

db_connection.close()
