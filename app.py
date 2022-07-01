from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# def get_product(product_id):
#     conn = get_db_connection()
#     product = conn.execute('SELECT * FROM products WHERE id = ?',
#                         (product_id,)).fetchone()
#     conn.close()
#     if product is None:
#         abort(404)
#     return product
    
##############################################
## CLASS DEFINITIONS
##############################################
class User(object):
    def __init__(self, user_id=None, username='Anonymous', password=None, email=None, address=None, bank_details=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.address = address
        self.bank_details = bank_details

    def reset(self):
        self.id = None
        self.username = 'Anonymous'
        self.password = None
        self.email = None
        self.address = None
        self.bank_details = None

    def find_user_by_username(self):
        conn = get_db_connection()
        user_record = conn.execute('SELECT * FROM users WHERE username=?', (self.username,)).fetchone()        
        conn.close()
        return user_record

    def get_reviews(self):
        conn = get_db_connection()
        reviews = conn.execute('SELECT * FROM reviews WHERE user_id = ? ORDER BY date', (self.id,)).fetchall()
        conn.close()
        return reviews
    
    def add(self):
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password, email, address, bank_details) VALUES (?, ?, ?, ?, ?)',
                            ( self.username, self.password, self.email, self.address, self.bank_details))
        conn.commit()
        conn.close()

        # conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
        #                     (username, password))
        #         conn.commit()
        #         user_records = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        #         conn.close()


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
    def __init__(self, product_id=None, name=None, description=None, price=None, merchant_id=None, distibution_center_id=None):
        
        if product_id != '':
            conn = get_db_connection()
            product = conn.execute('SELECT * FROM products WHERE id = ?',
                                (product_id,)).fetchone()
            conn.close()
            # if product is None:
            #     abort(404)
            self.id = product_id
            self.name = product['product_name']
            self.description = product['description']
            self.price = product['price']
        else:
            self.id = product_id
            self.name = name
            self.description = description
            self.price = price

        
    def get_all_products(self):
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products').fetchall()
        conn.close()
        return products

    def update(self):
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


class Order(object):
    def __init__(self, user_id=None):

        self.user = user_id
        self.transaction_id = ''
        self.products = []
    
    def set_transaction_id(self,id):
        self.transaction_id = id

    def add_product(self, product_id):
        self.products.append(product_id)

    def remove_product(self, product_id):
        self.products.remove(product_id)  

    def get_product_list(self):
        conn = get_db_connection()
        
        sql = f'SELECT * FROM products WHERE id IN ({", ".join(["?"]*len(self.products))})'
        products = conn.execute(sql, self.products).fetchall()

        conn.commit()
        conn.close()  
        return products

    def get_orders(product_id, user_id):
        pass

    def commit_order(self):
        self.set_transaction_id(f"{self.user}_{datetime}")
        conn = get_db_connection()
        for product_id in self.products:
            product=Product(product_id)
            conn.execute('INSERT INTO orders (transaction_id, user_id, product_id, product_name, price) VALUES (?, ?, ?, ?, ?)',
                            (self.transaction_id, self.user, product.id, product.name, product.price))
            
        conn.commit()
        conn.close()

        #reset cart object
        self.transaction_id = ''
        self.products = []
       


    

##############################################
## Initializations an functions
##############################################
app = Flask(__name__)
app.config['SECRET_KEY'] = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
current_user = User(user_id=1, username='test')
cart = Order(user_id=current_user.id)




##############################################
## MAIN APPLICATION AND ROUTING
##############################################


@app.route('/')
def index():
    products = Product().get_all_products

    
    if request.args.get('signout'):
        flash('You have been signed out!')
        session.clear()  
        current_user.reset()  
        flash('{} {} {}'.format(current_user.id, current_user.username, current_user.password))

    else:
        flash('{} {} {}'.format(current_user.id, current_user.username, current_user.password))

    if request.args.get('update_cart'):
        flash("Shopping cart updated!")
        cart.add_product(request.args.get('update_cart'))
        
    return render_template('index.html', products=products, user=current_user.username, cart=cart)


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

           
            user_record = User(username=username).find_user_by_username()
            if  user_record == None:
                current_user.reset()
                current_user.id = user_record['id']
                current_user.username = user_record['username']
                current_user.password = user_record['password']
                current_user.add()
                flash('"{}" has been added'.format(current_user.username))
                
            if user_record['password'] != password:
                flash('Password is incorrect!')
            else:
                
                # current_user = User(user_records['id'], user_records['username'], user_records['password'])
                current_user.id = user_record['id']
                current_user.username = user_record['username']
                current_user.password = user_record['password']

                return redirect(url_for('index'))
            
    return render_template('sign-in.html', product=product)

######################################
########## Product Routing  ##########
######################################
@app.route('/<int:id>')
def product(id):
    product = Product(product_id=id)
    return render_template('product.html', product=product, user=current_user.username)

######################################
########## Create  Product ###########
######################################
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
            new_product.update()
            return redirect(url_for('index'))
    if current_user.username == 'Anonymous':
        flash("Sign in to sell a product on Wallymart.")
        return redirect(url_for('signin'))
    return render_template('create.html')

######################################
########## Edit Product #############
######################################
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    product = Product(product_id=id)

    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        price = request.form['price']
    
        if not product_name:
            flash('Title is required!')
        else:
            existing_product = Product(product_id=id,name=product_name, description=description, price=price)
            existing_product.update()
            return redirect(url_for('index'))

    # Make sure that only authenticated users can edit products
    elif current_user.username == 'Anonymous':
        flash("Sign in to edit a product.")
        return render_template('product.html', product=product)
    return render_template('edit.html', product=product)

######################################
########## Delete Product ############
######################################
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    product = Product(product_id=id)
    product.delete()
    flash('Product successfully deleted!')
    return redirect(url_for('index'))

######################################
########## Review Product ############
######################################
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

######################################
########## Shopping Cart ############
######################################
@app.route('/cart', methods=('GET', 'POST'))
def shopping_cart():
   
    
    # Make sure that only authenticated users can edit products
    if current_user.username == 'Anonymous':
        flash("Sign in to see your shopping cart.")
        return redirect(url_for('signin'))
    
    if request.method == 'POST' and request.args.get('checkout') == 'true':
        cart.commit_order()   

    elif request.method == 'POST' and request.args.get('remove_id') !='':
       
        remove_id = request.args.get('remove_id')
        product=Product(remove_id)
        
        cart.remove_product(remove_id)
        flash(f"{product.name} has been removed from your shopping cart.")

    

    products = cart.get_product_list()

    return render_template('shopping-cart.html', user=current_user.username, cart=cart, products=products)
