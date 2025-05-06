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
    {"name": "Jellycat Small Blossom Grey Bunny", "price": "19.99", "image": "grey_bunny.jpg"},
    {"name": "Jellycat Small Blossom Pink Bunny", "price": "19.99", "image": "pink_bunny.jpg"},
    {"name": "Jellycat Small Blossom White Bunny", "price": "19.99", "image": "white_bunny.jpg"},
]

c.executemany(
    'INSERT INTO items (name, price, image) VALUES (?,?,?)', 
    [(item["name"], item["price"], item["image"]) for item in items_for_sale]
)

conn.commit()
conn.close()