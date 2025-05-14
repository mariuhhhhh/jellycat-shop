import sqlite3

c.execute('DROP TABLE IF EXISTS items')

# Connect to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('items_for_sale.db')

# Create a cursor object to interact with the database
c = conn.cursor()


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
        "description": "Blossom Bashful Silver Bunny loves flowers so much that she wears them on her paws and ears! She’s happiest of all when rolling through the buttercups and whizzing down hills!<br>Product Details: Dimensions: 67cm x 31cm x 22cm<br>Sitting Height: 56<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye<br>Environmental impact: 4.705 kg CO₂e",
        "environmental_impact": "4.705 kg CO₂e"

    },
    {
        "name": "Jellycat Small Blossom Pink Bunny",
        "price": 19.99,
        "image": "pink_bunny.jpg",
        "description": "Blossom Blush Bunny can't wait to join the picnic - this bobtail bopper has even brought some flowers! Dreamy-soft in warm peach fur, with a pink bobble nose and blossom ears and paws, this bunny brings the springtime.<br>Product Details: Dimensions: 67cm x 31cm x 22cm<br>Sitting Height: 56<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye<br> Environmental impact:4.705 kg CO₂e",
        "environmental_impact": "4.705 kg CO₂e"
    },
    {
        "name": "Jellycat Small Blossom White Bunny",
        "price": 19.99,
        "image": "white_bunny.jpg",
        "description": "The sunshine’s here and deliciously soft Blossom Bashful Cream Bunny is celebrating with pretty patterns in her flopsy ears! She’s even got flowers on her furry feet! With creamy, squishy paws and a friendly smile, she’s the best picnic pal ever!<br>Product Details: Dimensions: 67cm x 31cm x 22cm<br>Sitting Height: 56<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye<br> Environmental Impact: 4.705 kg CO₂e ",
        "environmental_impact": "4.705 kg CO₂e"
    },
    {
        "name": "Bartholomew Bear 'Bumblebee'",
        "price": 45,
        "image": "bumble_bear.jpg",
        "description": "Bartholomew Bear ‘Bumblebee’ is all snuggle, no sting. Our most-loved toffee bear is spreading springtime joy in a stripey bee costume, which can be removed. With a fixed antennae headband, this is a bear you can snuggle for all seasons.<br>Product Details: Dimensions: 26cm x 14cm x 14cm<br>Sitting Height: 22<br>Wingspan: 11<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye, Removable Costume, Hat attached<br> Environmental Impact: 4.7kg CO₂e ",
        "environmental_impact": "4.7 kg CO₂e"
    },
    {
        "name": "Albee Bee",
        "price": 25,
        "image": "bumble_bee.jpg",
        "description": "Albee Bee is the happiest little bumble. In thick yellow and black striped fur with little charcoal legs, Albee has a matching face with curved antennae. With a big, stitched smile and soft cream wings, Albee spreads springtime joy all year long!<br>Product Details: Dimensions: 16cm x 11cm x 12cm<br>Sitting Height: 13<br>Wingspan: 9<br>Main Materials: Polyester<br>Inner Filling: Polyester Fibres<br>PE Beans<br>Hard Eye<br> Environmental Impact: 1.5kg CO₂e ",
        "environmental_impact": "1.5 kg CO₂e"
    }
]

c.executemany(
    'INSERT INTO items (name, price, image, description, environmental_impact) VALUES (?,?,?,?,?)',
    [(item["name"], item["price"], item["image"], item["description"], item["environmental_impact"]) for item in items_for_sale]
)
# Function to check if the item already exists
def item_exists(item_name):
    c.execute("SELECT 1 FROM items WHERE name = ?", (item_name,))
    return c.fetchone() is not None

# Insert items into the database
for item in items_for_sale:
    try:
        c.execute('''
                  INSERT INTO items (name, price, image, description, environmental_impact)
                  VALUES (?,?,?,?,?)
                  ''', (item["name"], item["price"], item["image"], item["description"], item["environmental_impact"]))
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")


conn.commit()
conn.close()