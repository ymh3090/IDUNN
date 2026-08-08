import sqlite3
con = sqlite3.connect("tutorial.db")


# cursor initailization
cur = con.cursor()


# cur.execute("CREATE TABLE movie(title, year, score)")
data = [
    ("Monty Python Live at the Hollywood Bowl",1982,7.9),
    ("Monty Python's The Meaning of Life1",1983,7.5),
    ("Monty Python's Life of Brian",1979,8.0),
]


cur.executemany("INSERT INTO movie VALUES(?,?,?)", data)
con.commit()  # Remember to commit the transaction after executing INSERT.


# con.commit()
con.close()
# con = sqlite3.connect("tutorial.db")