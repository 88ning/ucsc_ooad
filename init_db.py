import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO products (product_name, description, price) VALUES (?, ?, ?)",
            ('First product', 'Tie your shoes in the dark.', '$1')
            )

cur.execute("INSERT INTO products (product_name, description, price) VALUES (?, ?, ?)",
            ('Second product', 'Vaccuum your entire house while you sleep.', '$2')
            )


cur.execute('INSERT INTO users (username, password) VALUES (?, ?)',
             ('test1', 'test')
            )
cur.execute('INSERT INTO users (username, password) VALUES (?, ?)',
             ('test2', 'test')
            )

cur.execute('INSERT INTO users (username, password) VALUES (?, ?)',
             ('test3', 'test')
            )

cur.execute('INSERT INTO users (username, password) VALUES (?, ?)',
             ('test4', 'test')
            )

cur.execute('INSERT INTO users (username, password) VALUES (?, ?)',
             ('test5', 'test')
            )


cur.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
             (1, 1, 5, 'amazing', '01/19/2022 18:25:40')
            )
cur.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
             (1, 1, 5, 'amazing', '02/19/2022 18:25:40')
            )

cur.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
             (2, 1, 5, 'Great product!', '03/19/2022 18:25:40')
            )

cur.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
             (2, 1, 1, 'Did not like it. Too noisy.', '01/19/2021 18:25:40')
            )

cur.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
             (3, 1, 3, 'It was fine.', '02/19/2022 18:25:40')
            )

cur.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
             (4, 1, 5, 'Definitely does the job.', '05/07/2022 18:25:40')
            )

cur.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
             (5, 1, 2, 'Too expensive.', '05/07/2022 17:25:40')
            )


connection.commit()
connection.close()