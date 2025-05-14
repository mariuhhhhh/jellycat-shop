from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Regexp
from flask_bootstrap import Bootstrap
import sqlite3

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"

# Session cookie security settings
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False
)

# Retrieve all items from the database

def get_all_items():

    conn = sqlite3.connect('items_for_sale.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    return items

# Get a single item by ID
def get_item_by_id(item_id):
    conn = sqlite3.connect('items_for_sale.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))



    item = c.fetchone()
    conn.close()
    return item

# Form for adding items to basket
class BasketForm(FlaskForm):
    quantity = IntegerField('Quantity: ', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Basket')

# Home page showing all items with sorting
@app.route('/')
def galleryPage():
    sort_by = request.args.get('sort', default='name')
    items_for_sale = get_all_items()

    print(f"Items fetched: {items_for_sale}")

    if sort_by == 'price':
        items_for_sale.sort(key=lambda item: item['price'])
    elif sort_by == 'carbon':
        items_for_sale.sort(key=lambda item: float(item['environmental_impact'].split()[0]))
    else:
        items_for_sale.sort(key=lambda item: item['name'].lower())

    return render_template('index.html', items_for_sale=items_for_sale)

# In-memory reviews storage
reviews_db = {}

# Single product view with form and review handling
@app.route('/product/<int:item_id>', methods=['GET', 'POST'])
def singleProductPage(item_id):
    form = BasketForm()
    item = get_item_by_id(item_id)
    reviews = reviews_db.get(item_id, [])

    if form.validate_on_submit():
        quantity = form.quantity.data

        # Create basket in session if it doesn't exist
        if 'basket' not in session:
            session['basket'] = []

        # Add item to basket
        session['basket'].append({
            'id': item_id,
            'name': item['name'],
            'price': float(item['price']),
            'quantity': quantity
        })
        session.modified = True

        return redirect(url_for('viewBasket'))

    return render_template('SingleTech.html', item=item, form=form, reviews=reviews)

# Handle new review submission
@app.route('/item/<int:item_id>/review', methods=['POST'])
def submit_review(item_id):
    author = request.form.get('author')
    content = request.form.get('content')

    if not author or not content:
        flash("All fields are required!")
        return redirect(url_for('singleProductPage', item_id=item_id))

    new_review = {'author': author, 'content': content}
    reviews_db.setdefault(item_id, []).append(new_review)

    return redirect(url_for('singleProductPage', item_id=item_id))

# Route to add an item to the basket (1 quantity by default)
@app.route('/add_to_basket/<int:item_id>', methods=['POST'])
def add_to_basket(item_id):
    basket = session.get('basket', [])
    item = get_item_by_id(item_id)

    if 'basket' not in session:
        session['basket'] = []

    existing_item = next((i for i in session['basket'] if i['id'] == item_id), None)
    
    if existing_item:
        existing_item['quantity'] += 1
    else:
        session['basket'].append({
            'id': item_id,
            'name': item['name'],
            'price': float(item['price']),
            'quantity': 1
        })

    session['basket'] = basket
    session.modified = True
    flash("Added to basket!")

    return redirect(url_for('galleryPage'))

# View the basket and calculate total
@app.route('/basket')
def viewBasket():
    basket = session.get('basket', [])
    total_price = round(sum(item['price'] * item['quantity'] for item in basket), 2)
    return render_template('basket.html', basket=basket, total_price=total_price)

# Remove item from basket
@app.route('/remove_from_basket/<int:item_id>', methods=['POST'])
def remove_from_basket(item_id):
    if 'basket' in session:
        basket = session['basket']
        session['basket'] = [item for item in basket if item['id'] != item_id]
        session.modified = True
    return redirect(url_for('viewBasket'))

# Route to clear the entire basket
@app.route('/clear_basket', methods=['POST'])
def clear_basket():
    session.pop('basket', None)  # Safely remove 'basket' from session
    session.modified = True
    return redirect(url_for('viewBasket'))

@app.route('/update_quantity/<int:item_id>', methods=['POST'])
def update_quantity(item_id):
    quantity = int(request.form.get('quantity', 1))

    basket = session.get('basket', [])

    for item in basket:
        if item['id'] == item_id:
            item['quantity'] = quantity
            break

    session['basket'] = basket
    return redirect(url_for('viewBasket'))



# Return item description as JSON (for dynamic loading)
@app.route('/item-details/<int:item_id>')
def item_details(item_id):
    item = get_item_by_id(item_id)
    if item:
        item_dict = dict(item)
        description = item_dict.get('description')
        if description:
            return jsonify({'description': description})
    return jsonify({'error': 'Item not found'}), 404

# Checkout form with simple card validation
class CheckoutForm(FlaskForm):
    name = StringField('Name on Card', validators=[InputRequired()])
    card_number = StringField('Credit Card Number', validators=[
        InputRequired(),
        Regexp(r'^\s*\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\s*$', message="Must be a valid 16-digit card number")
    ])
    expiry = StringField('Expiry Date (MM/YY)', validators=[
        InputRequired(),
        Regexp(r'^(0[1-9]|1[0-2])\/\d{2}$', message="Enter a valid expiry date (MM/YY)")
    ])
    cvv = StringField('CVV', validators=[
        InputRequired(),
        Regexp(r'^\d{3}$', message="Enter a valid 3-digit CVV")
    ])
    submit = SubmitField('Pay Now')

# Checkout page handler
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    basket = session.get('basket', [])
    total_price = round(sum(item['price'] * item['quantity'] for item in basket), 2)

    if form.validate_on_submit():
        flash("Payment successful! This is a simulated checkout.")
        return render_template('confirmation.html', total_price=total_price)

    return render_template('checkout.html', form=form, total_price=total_price)

# Start the app
if __name__ == '__main__':
    app.run(debug=True)


items_for_sale = [
    {"name": "Jellycat Small Blossom Grey Bunny", "price": "19.99", "image": "grey_bunny.jpg"},
    {"name": "Jellycat Small Blossom Pink Bunny", "price": "19.99", "image": "pink_bunny.jpg"},
    {"name": "Jellycat Small Blossom White Bunny", "price": "19.99", "image": "white_bunny.jpg"},
]

def get_item_by_id(item_id):
    conn = sqlite3.connect('items_for_sale.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    conn.close()
    return item

# Form for adding items to basket
class BasketForm(FlaskForm):

    quantity = IntegerField('Quantity: ', validators=[DataRequired(), NumberRange(min=1)])

    submit = SubmitField('Add to Basket')

# Home page showing all items with sorting
@app.route('/')
def galleryPage():
    sort_by = request.args.get('sort', default='name')
    items_for_sale = get_all_items()

    if sort_by == 'price':
        items_for_sale.sort(key=lambda item: item['price'])
    elif sort_by == 'carbon':
        items_for_sale.sort(key=lambda item: float(item['environmental_impact'].split()[0]))
    else:
        items_for_sale.sort(key=lambda item: item['name'].lower())


    return render_template('index.html', items_for_sale=items_for_sale)

# In-memory reviews storage
reviews_db = {}

# Single product view with form and review handling
@app.route('/product/<int:itemId>', methods=['GET', 'POST'])
def singleProductPage(itemId):
    form = BasketForm()
    item = get_item_by_id(itemId)
    reviews = reviews_db.get(itemId, [])

    if form.validate_on_submit():
        quantity = form.quantity.data

        # Create basket in session if it doesn't exist
        if 'basket' not in session:
            session['basket'] = []

        # Add item to basket
        session['basket'].append({'id': itemId, 'name': item['name'], 'quantity': quantity})
        session.modified = True

        return redirect(url_for('viewBasket'))

    return render_template('SingleTech.html', item=item, form=form, reviews=reviews)

# Handle new review submission
@app.route('/item/<int:item_id>/review', methods=['POST'])
def submit_review(item_id):
    author = request.form.get('author')
    content = request.form.get('content')

    if not author or not content:
        flash("All fields are required!")
        return redirect(url_for('singleProductPage', item_id=item_id))

    new_review = {'author': author, 'content': content}
    reviews_db.setdefault(item_id, []).append(new_review)

    return redirect(url_for('singleProductPage', item_id=item_id))


@app.route('/basket')
def viewBasket():
    basket = session.get('basket', [])
    return render_template('basket.html', basket=basket)

# Route to add an item to the basket (1 quantity by default)
@app.route('/add_to_basket/<int:item_id>', methods=['POST'])
def add_to_basket(item_id):
    item = get_item_by_id(item_id)

    if 'basket' not in session:
        session['basket'] = []

    existing_item = next((i for i in session['basket'] if i['id'] == item_id), None)
    
    if existing_item:
        existing_item['quantity'] += 1
    else:
        session['basket'].append({
            'id': item_id,
            'name': item['name'],
            'price': float(item['price']),
            'quantity': 1
        })

    session.modified = True
    return redirect(url_for('galleryPage'))

# View the basket and calculate total
@app.route('/basket')
def viewBasket():
    basket = session.get('basket', [])
    total_price = round(sum(item['price'] * item['quantity'] for item in basket), 2)
    return render_template('basket.html', basket=basket, total_price=total_price)


# Remove item from basket
@app.route('/remove_from_basket/<int:item_id>', methods=['POST'])
def remove_from_basket(item_id):
    if 'basket' in session:
        basket = session['basket']
        session['basket'] = [item for item in basket if item['id'] != item_id]
        session.modified = True
    return redirect(url_for('viewBasket'))

# Return item description as JSON (for dynamic loading)
@app.route('/item-details/<int:item_id>')
def item_details(item_id):
    item = get_item_by_id(item_id)

    if item:
        item_dict = dict(item)
        description = item_dict.get('description')
        if description:
            return jsonify({'description': description})
    return jsonify({'error': 'Item not found'}), 404

# Checkout form with simple card validation
class CheckoutForm(FlaskForm):
    name = StringField('Name on Card', validators=[InputRequired()])
    card_number = StringField('Credit Card Number', validators=[
        InputRequired(),
        Regexp(r'^\s*\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\s*$', message="Must be a valid 16-digit card number")
    ])
    expiry = StringField('Expiry Date (MM/YY)', validators=[
        InputRequired(),
        Regexp(r'^(0[1-9]|1[0-2])\/\d{2}$', message="Enter a valid expiry date (MM/YY)")
    ])
    cvv = StringField('CVV', validators=[
        InputRequired(),
        Regexp(r'^\d{3}$', message="Enter a valid 3-digit CVV")
    ])
    submit = SubmitField('Pay Now')

# Checkout page handler
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    basket = session.get('basket', [])
    total_price = round(sum(item['price'] * item['quantity'] for item in basket), 2)

    if form.validate_on_submit():
        flash("Payment successful! This is a simulated checkout.")
        return render_template('confirmation.html', total_price=total_price)

    return render_template('checkout.html', form=form, total_price=total_price)

# Start the app
if __name__ == '__main__':
    app.run(debug=True)

