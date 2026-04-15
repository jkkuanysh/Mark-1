import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="postgres",   # или твоя база
    user="postgres",
    password="your_password",
    port="5432"
)

cur = conn.cursor()

cur.execute("SELECT version();")
print(cur.fetchone())

cur.close()
conn.close()