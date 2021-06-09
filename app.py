from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():
    return render_template('index.html', page="Home")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product, page = product["name"])

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(code)

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', page = "Login")

@app.route('/pastorders', methods = ['GET'])
def pastorders():
    actualorderlist = []
    orderlist, ordercount = db.display_orders(session.get("user")["username"])
    for order in orderlist:
        actualorderlist.append(order)
        order["total"] = 0
        for item in order["details"]:
            order["total"] += item["subtotal"]
    return render_template('pastorders.html', orderlist = actualorderlist, ordercount = ordercount, page = "Past Orders")

@app.route('/changepassword', methods = ["GET","POST"])
def changepassword():
    if request.method == "GET":
        return render_template ('changepassword.html', message = None, success = None, page = "Change Password")
    else:
        changepasswordresult, success = authentication.changepassword(session.get("user")["username"],request.form.get("oldpass"),request.form.get("newpass"),request.form.get("connewpass"))
        return render_template('changepassword.html',message = changepasswordresult, success = success, page = "Change Password")

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        return render_template('login.html', page = "Invalid username or password. Please try again.")
        #return redirect('/login')

@app.route('/updateQty', methods = ['GET','POST'])
def updateQty():
    cart1 = session["cart"]
    for product in request.form.keys():
        if request.form.get(product) is not "":
            cart1[product]["qty"] += int(request.form.get(product))
            if cart1[product]["qty"] <= 0:
                cart1.pop(product)
            else:
                cart1[product]["subtotal"] = cart1[product]["price"] * cart1[product]["qty"]

    session["cart"] = cart1
    return redirect('/cart')

@app.route('/removeItem', methods = ['GET'])
def removeItem():
    code = request.args.get('code','')
    cart1 = session["cart"]
    cart1.pop(code)
    session["cart"] = cart1
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart(request.args.get("address"))
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a
    # quantity of 1 for now
    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]
    item["code"] = int(code)
    item["price"] = product["price"]
    if(session.get("cart") is None):
        session["cart"]={}
    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html', page = "Cart")
