from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask import jsonify
import sqlite3

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"

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
    quantity = IntegerField('Quantity: ',validators = [DataRequired()])
    submit = SubmitField('Add to Basket')

@app.route('/')
def galleryPage():
    items_for_sale = get_all_items()
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
        session['basket'].append({'id': itemId, 'name': item['name'], 'quantity': quantity})
        session.modified = True

        return redirect(url_for('viewBasket'))

    return render_template('SingleTech.html', item=item, form=form)

@app.route('/basket')
def viewBasket():
    basket = session.get('basket', [])
    return render_template('basket.html', basket=basket)

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
    if item and hasattr(item, 'description'):
        return {'description': item.description}
    return {'error': 'Item not found'}, 404


if __name__ == '__main__':
    app.run(debug=True)
