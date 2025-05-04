from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"

items_for_sale = [
    {"name": "Jellycat Small Blossom Grey Bunny", "price": "19.99", "image": "grey_bunny.jpg"},
    {"name": "Jellycat Small Blossom Pink Bunny", "price": "19.99", "image": "pink_bunny.jpg"},
    {"name": "Jellycat Small Blossom White Bunny", "price": "19.99", "image": "white_bunny.jpg"},
]

class BasketForm(FlaskForm):
    quantity = IntegerField('Quantity: ',validators = [DataRequired()])
    submit = SubmitField('Add to Basket')

@app.route('/')
def galleryPage():
    return render_template('index.html', items_for_sale=items_for_sale)

@app.route('/product/<int:itemId>',methods=['GET','POST'])
def singleProductPage(itemId):
    form = BasketForm()
    if form.validate_on_submit():
        quantity = form.quantity.data
        item = items_for_sale[itemId]
        return render_template('AddedToBasket.html', item=item, quantity=quantity)
    else:
        item = items_for_sale[itemId]
        return render_template('SingleTech.html', item=item, form=form)

if __name__ == '__main__':
    app.run(debug=True)
