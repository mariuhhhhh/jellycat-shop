import sqlite3

# connect to a SQLite database (or create it)
conn = sqlite3.connect('items_for_sale.db')
c = conn.cursor()

# create the table
c.execute('''
          CREATE TABLE IF NOT EXISTS items  (
          id INTEGER PRIMARY KEY AUTOINCREMENT, 
          name TEXT NOT NULL,
          price TEXT NOT NULL,
          image TEXT NOT NULL
        ) 
''')

# insert items
items_for_sale = [
    {"Jellycat Small Blossom Grey Bunny", "19.99", "grey_bunny.jpg"},
    {"Jellycat Small Blossom Pink Bunny", "19.99",  "pink_bunny.jpg"},
    {"Jellycat Small Blossom White Bunny", "19.99", "white_bunny.jpg"},
]

c.executemany('INSERT INTO items (name, price, image) VALUES (?,?,?)', items_for_sale)

conn.commit()
conn.close()