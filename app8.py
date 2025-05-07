from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Regexp
from flask import render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask import jsonify
import sqlite3

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"

# Secure session cookie configuration
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # Use 'Strict' if you want more isolation
    SESSION_COOKIE_SECURE=False  # Set to True if using HTTPS
)

# function to get items from the database
def get_all_items():
    conn = sqlite3.connect('items_for_sale.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    return items

def get_item_by_id(item_id):
    conn = sqlite3.connect('items_for_sale.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()
    conn.close()
    return item

class BasketForm(FlaskForm):
    quantity = IntegerField('Quantity: ',validators = [DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Basket')

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

@app.route('/product/<int:itemId>',methods=['GET','POST'])
def singleProductPage(itemId):
    form = BasketForm()
    item = get_item_by_id(itemId)

    if form.validate_on_submit():
        quantity = form.quantity.data

        # Initialize basket if it doesn't exist
        if 'basket' not in session:
            session['basket'] = []

        # Add item to basket
        session['basket'].append({
            'id': itemId,
            'name': item['name'],
            'price': float(item['price']),
            'quantity': quantity
        })
        session.modified = True

        return redirect(url_for('viewBasket'))

    return render_template('SingleTech.html', item=item, form=form)

@app.route('/add_to_basket/<int:item_id>', methods=['POST'])
def add_to_basket(item_id):
    item = get_item_by_id(item_id)

    # Initialize basket if it doesn't exist
    if 'basket' not in session:
        session['basket'] = []

    # Check if item already in basket
    existing_item = next((i for i in session['basket'] if i['id'] == item_id), None)
    
    if existing_item:
        existing_item['quantity'] += 1  # Increment quantity if item is already in basket
    else:
        session['basket'].append({
            'id': item_id,
            'name': item['name'],
            'price': float(item['price']),
            'quantity': 1
        })

    session.modified = True
    return redirect(url_for('galleryPage'))

@app.route('/basket')
def viewBasket():
    basket = session.get('basket', [])
    
    total_price = 0
    total_price = round(sum(item['price'] * item['quantity'] for item in basket), 2)


    return render_template('basket.html', basket=basket, total_price=total_price)

@app.route('/remove_from_basket/<int:item_id>', methods=['POST'])
def remove_from_basket(item_id):
    # Check if the basket exists in the session
    if 'basket' in session:
        # Find the item in the basket
        basket = session['basket']
        
        # Find and remove the item with the given ID
        session['basket'] = [item for item in basket if item['id'] != item_id]
        
        # Mark the session as modified
        session.modified = True
        
    # After removal, redirect to the basket page
    return redirect(url_for('viewBasket'))

@app.route ('/item-details/<int:item_id>')
def item_details(item_id):
    item = get_item_by_id(item_id)
    print(f"fetched item: {item}")

    if item:
        item_dict = dict(item)
        print(f"Converted to dict: {item_dict}")  
        description = item_dict.get('description')
        if description:
            return jsonify({'description': description})

    return jsonify({'error': 'Item not found'}), 404

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

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    
    # Assume basket and total are calculated from session
    basket = session.get('basket', [])
    total_price = round(sum(item['price'] * item['quantity'] for item in basket), 2)

    if form.validate_on_submit():
        # Flash confirmation (or redirect to confirmation page)
        flash("Payment successful! This is a simulated checkout.")
        return render_template('confirmation.html', total_price=total_price)

    return render_template('checkout.html', form=form, total_price=total_price)


if __name__ == '__main__':
    app.run(debug=True)
