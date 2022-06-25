from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?',
                        (product_id,)).fetchone()
    conn.close()
    if product is None:
        abort(404)
    return product
    
##############################################
## CLASS DEFINITIONS
##############################################
class User(object):
    def __init__(self, user_id=None, username='Anonymous', password=None):
        self.id = user_id
        self.username = username
        self.password = password

    def reset(self):
        self.id = None
        self.username = 'Anonymous'
        self.password = None

    def get_reviews(self):
        pass

class Review(object):
    def __init__(self, review_id=None, product_id=None, user=None, rating=None, feedback=None):
        self.id = review_id
        self.user= user
        self.product_id = product_id
        self.rating = rating
        self.feedback = feedback
        self.date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    def add(self):
        conn = get_db_connection()
        conn.execute('INSERT INTO reviews (user_id, product_id, rating, feedback, date) VALUES (?, ?, ?, ?, ?)',
                            ( self.user, self.product_id, self.rating, self.feedback, self.date))
        conn.commit()
        conn.close()
    
    


class Product(object):
    def __init__(self, product_id=None, name=None, description=None, price=None):
        self.id = product_id
        self.name = name
        self.description = description
        self.price = price
        

    def update_db(self):
            conn = get_db_connection()
            if conn.execute('SELECT * FROM products WHERE id = ?', (self.id,)).fetchone() == None:
                conn.execute('INSERT INTO products (product_name, description, price) VALUES (?, ?, ?)',
                            ( self.name, self.description, self.price))
            else:
                conn.execute('UPDATE products SET product_name = ?, description = ?, price = ?'
                         ' WHERE id = ?',
                       (self.name, self.description, self.price, self.id))
            conn.commit()
            conn.close()
    
    def delete(self):
        conn = get_db_connection()
        conn.execute('DELETE from products WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
    
    def get_reviews(self):
        conn = get_db_connection()
        reviews = conn.execute('SELECT * FROM reviews WHERE product_id = ? ORDER BY date', (self.id,)).fetchall()
        conn.close()
        return reviews

    def get_quantity(id):
        pass


##############################################
## Initializations an functions
##############################################
app = Flask(__name__)
app.config['SECRET_KEY'] = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
current_user = User()




##############################################
## MAIN APPLICATION AND ROUTING
##############################################


@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    if request.args.get('signout'):
        flash('You have been signed out!')
        session.clear()  
        current_user.reset()  
        flash('{} {} {}'.format(current_user.id, current_user.username, current_user.password))

    else:
        flash('{} {} {}'.format(current_user.id, current_user.username, current_user.password))
    
    return render_template('index.html', products=products, user=current_user.username)

######################################
########## Product Routing  ##########
######################################
@app.route('/<int:product_id>')
def product(product_id):
    product = get_product(product_id)
    return render_template('product.html', product=product)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
        
        
        if not product_name:
            flash('Title is required!')
        else:
            new_product = Product(name=product_name, description=description,price=price)
            new_product.update_db()
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    product = get_product(id)

    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
    
        if not product_name:
            flash('Title is required!')
        else:
            existing_product = Product(product_id=id,name=product_name, description=description, price=price)
            existing_product.update_db()
            return redirect(url_for('index'))
    return render_template('edit.html', product=product)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    product = Product(product_id=id)
    product.delete()
    flash('Product successfully deleted!')
    return redirect(url_for('index'))

##############################
########## Reviews  ##########
##############################
@app.route('/<int:id>/review', methods=('GET', 'POST'))
def review(id):
    product = Product(product_id=id)
    reviews = product.get_reviews()
    if request.method == 'POST':
        feedback = request.form['feedback']
        rating = request.form['rating']

        review = Review(product_id=id, user=current_user.username, feedback=feedback, rating=rating)
        review.add()
        flash("Review added!")
        return render_template('review.html', product=product, reviews=reviews, user=current_user.username)

    if request.method == 'GET':
        product = Product(product_id=id)
        reviews = product.get_reviews()
        

    return render_template('review.html', product=product, reviews=reviews, user=current_user.username)


##############################
########## Sign In  ##########
##############################

@app.route('/sign-in', methods=('GET', 'POST'))
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        if not username:
            flash('Username is required!')
        if not password:
            flash('Password is required!')
        else:
            conn = get_db_connection()

           
            user_records = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
            if  user_records == None:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                            (username, password))
                conn.commit()
                user_records = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
                conn.close()
                flash('"{}" has been added'.format(username))
            if user_records['password'] != password:
                flash('Password is incorrect!')
            else:
                
                # current_user = User(user_records['id'], user_records['username'], user_records['password'])
                current_user.id = user_records['id']
                current_user.username = user_records['username']
                current_user.password = user_records['password']

                return redirect(url_for('index'))
            
    return render_template('sign-in.html', product=product)

