import pymysql

conn = pymysql.connect(
    host='162.144.14.110',
    user='thescaus_AbiFranklin',
    password='',
    database='thescaus_PythonDemo'
)

cursor = conn.cursor()

cursor.execute("SELECT DATABASE()")
db = cursor.fetchone()
print(f"Connected to database: {db}")

cursor.close()
conn.close()
