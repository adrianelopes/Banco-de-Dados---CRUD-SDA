import psycopg2
con = psycopg2.connect(
    host='localhost',
    database='crud_bd',
    user='adriane',
    password='al123dri4'
)
cur = con.cursor()

cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100),
                email VARCHAR(100)
            )
        """)
con.commit()

cur.execute("INSERT INTO usuarios (nome, email) VALUES (%s, %s)", ('Renan', 'Renan@email'))
con.commit()
cur.execute("INSERT INTO usuarios (nome, email) VALUES (%s, %s)", ('Adriane', 'Adriane@email'))
con.commit()

cur.execute("SELECT * FROM usuarios")
con.commit()

for row in cur.fetchall():
    print(row)