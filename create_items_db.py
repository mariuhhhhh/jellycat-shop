import sqlite3

# connect to a SQLite database (or create it)
conn = sqlite3.connect('items_for_sale.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS items')

# create the table
c.execute('''
          CREATE TABLE IF NOT EXISTS items  (
          id INTEGER PRIMARY KEY AUTOINCREMENT, 
          name TEXT NOT NULL,
          price TEXT NOT NULL,
          image TEXT NOT NULL,
          description TEXT NOT NULL,
          environmental_impact TEXT NOT NULL
          ) 
    ''')


# insert items with descriptions
items_for_sale = [
    {
        "name": "Jellycat Small Blossom Grey Bunny",
        "price": 19.99,
        "image": "grey_bunny.jpg",
        "description": "Product Details: Dimensions: 67cm x 31cm x 22cm<br>Sitting Height: 56<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye",
        "environmental_impact": "4.705 kg CO₂e"

    },
    {
        "name": "Jellycat Small Blossom Pink Bunny",
        "price": 19.99,
        "image": "pink_bunny.jpg",
        "description": "Product Details: Dimensions: 67cm x 31cm x 22cm<br>Sitting Height: 56<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye",
        "environmental_impact": "4.705 kg CO₂e"
    },
    {
        "name": "Jellycat Small Blossom White Bunny",
        "price": 19.99,
        "image": "white_bunny.jpg",
        "description": "Product Details: Dimensions: 67cm x 31cm x 22cm<br>Sitting Height: 56<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye",
        "environmental_impact": "4.705 kg CO₂e"
    },
    {
        "name": "Bartholomew Bear 'Bumblebee'",
        "price": 45,
        "image": "bumble_bear.jpg",
        "description": "Product Details: Dimensions: 26cm x 14cm x 14cm<br>Sitting Height: 22<br>Wingspan: 11<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye, Removable Costume, Hat attached",
        "environmental_impact": "4.705 kg CO₂e" 
    },
    {
        "name": "Albee Bee",
        "price": 25,
        "image": "bumble_bee.jpg",
        "description": "Product Details: Dimensions: 16cm x 11cm x 12cm<br>Sitting Height: 13<br>Wingspan: 9<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye",
        "environmental_impact": "4.705 kg CO₂e"
    }
]

c.executemany(
    'INSERT INTO items (name, price, image, description, environmental_impact) VALUES (?,?,?,?,?)', 
    [(item["name"], item["price"], item["image"], item["description"], item["environmental_impact"]) for item in items_for_sale]
)

conn.commit()
conn.close()