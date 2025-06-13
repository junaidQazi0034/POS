from flask import Flask, render_template, request, redirect, url_for, session
import DatabaseHelper as db
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '111222'


###============================= USERS ========================###
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/homePage')
def view_home():
    return render_template("Home.html")

@app.route('/adminLogin', methods=['GET', 'POST'])
def admin_login():
    msg=None
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        isLoginValid = db.loginAdmin(username, password)
        if isLoginValid:
            session["username"]=username
            session["usertype"]="Admin"
            return redirect(url_for("view_users"))
        else:
            msg="Invalid Username/password"
    return render_template('adminLogin.html', message=msg)

@app.route('/userLogin', methods=['GET', 'POST'])
def user_login():
    msg=None
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        userType = request.form.get('userType')
        isLoggedin = db.loginUser(username, password,userType)
        if isLoggedin:
            session["username"]=username
            session["usertype"]=userType
            return redirect(url_for("view_home"))
        else:
            msg="Invalid Username/password"
    return render_template("userLogin.html", message=msg)

@app.route('/registerUser',  methods=['GET','POST'])
def register_user():
    msg=None
    if request.method=='POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confrimPassword = request.form.get('confirmPassword')
        age = request.form.get('age')
        gender = request.form.get('gender')
        userType = request.form.get('userType')
        if password != confrimPassword:
            msg ="Password and confirm password does not match"
        else:
            db.registeruser(name,username,password,gender,age,userType)
            msg ="registeration successful"
    return render_template("registerUser.html", message =msg)            

@app.route('/addUser',  methods=['GET','POST'])
def add_user():
    msg=None
    if request.method=='POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        userType = request.form.get('userType')
        db.registeruser(name,username,password,gender,age,userType)
        msg ="New User Added"
        return redirect(url_for("view_users"))
    return render_template("addNewUser.html", message =msg)            

@app.route('/viewUsers')
def view_users():
    users_data=db.getAllUsers()
    return render_template('users.html', users=users_data)

@app.route('/updateUser/<int:uid>', methods=['GET','POST'])
def update_user(uid):
    if request.method=="POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        gender = request.form.get("gender")
        age = request.form.get("age")
        userType = request.form.get("userType")
        db.updateUser(name, username, password, gender, age,userType,uid)
        return redirect(url_for("view_users"))
    else:
        userdata = db.getUserData(uid)
        return render_template('updateUser.html', user=userdata)  

@app.route('/deleteUser/<int:uid>', methods=['POST','GET'])
def delete_user(uid):
    db.deleteUser(uid)
    return redirect(url_for("view_users"))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('usertype', None)
    return redirect(url_for('user_login'))

####---------------------PRODUCTS -------------------------###
@app.route('/addProduct',  methods=['GET','POST'])
def add_product():
    msg=None
    if request.method=='POST':
        name = request.form.get('name')
        size = request.form.get('size')
        category = request.form.get('category')
        unitPrice = request.form.get('unitPrice')
        db.addProduct(name,size,category,unitPrice)
        msg ="New Product Added"
        return redirect(url_for("view_products"))
    return render_template("addNewProduct.html", message =msg)            

@app.route('/viewProducts')
def view_products():
    # Fetch products from the database
    products_data=db.getAllProducts()
    # Render the HTML page with Bootstrap
    return render_template('products.html', products=products_data)

@app.route('/updateProduct/<int:pid>', methods=['GET','POST'])
def update_product(pid):
    if request.method=="POST":
        name = request.form.get("name")
        size = request.form.get("size")
        category = request.form.get("category")
        unitPrice = request.form.get("unitPrice")
        db.updateProduct(name, size, category, unitPrice,pid)
        return redirect(url_for("view_products"))
    else:
        productData = db.getproduct(pid)
        return render_template('updateProduct.html', product=productData)  

@app.route('/deleteProduct/<int:pid>', methods=['POST','GET'])
def delete_product(pid):
    db.deleteProduct(pid)
    return redirect(url_for("view_products"))

####---------------------CART-------------------------###
@app.route('/products')
def products_for_cart():
    products =db.getAllProducts()
    item_count=db.countCartItems()
    if item_count is None:
        order_id = db.getLastOrderID()
        item_count=(0,order_id)
        
    return render_template('products4cart.html', products=products, itemCount=item_count)

@app.route('/add2cart', methods=['POST'])
def add_to_cart():
    # Add product to cart
    if request.method=='POST':
        product_id = request.form.get('product_id')
        qty = request.form.get('qty')
        order_id = request.form.get('order_id')
        db.add2Cart(product_id, qty, order_id)    
    return redirect(url_for('products_for_cart'))

@app.route('/cart/<int:order_id>', methods=['POST','GET'])
def view_cart(order_id):
    order_date = db.getOrderDate(order_id)
    cart_items =db.getCartItems(order_id)
    return render_template('cart.html', items=cart_items, date=order_date, orderID=order_id)

@app.route('/removeCartItem/<int:cart_id>', methods=['POST','GET'])
def remove_from_cart(cart_id):
    db.deleteCartItem(cart_id)
    order_id = db.getLastOrderID()
    return redirect(url_for("view_cart", order_id=order_id))

@app.route('/completeCart/<int:order_id>', methods=['POST','GET'])
def complete_cart(order_id):
    db.updateCartCompletion(order_id)
    db.debitStock(order_id)
    db.newOrder()
    return redirect(url_for('products_for_cart'))

####---------------------INVENTORY-------------------------###
@app.route('/purchaseStock' , methods=['POST','GET'])
def purchase_stock():
    items = db.getAllProducts()
    if request.method=='POST':
        product_id = request.form.get('product')
        qty = request.form.get('qty')
       # order_id = 222
        db.creditStock(product_id,qty)
    stock= db.getStockQuantity()   
    return render_template('purchaseStock.html',items=items, stockItems=stock)

@app.route('/viewSales' , methods=['POST','GET'])
def view_sales():
    sales_list = db.getAllSales()
    return render_template('Sales.html', salesList=sales_list)

@app.route('/ViewSaleDetail/<int:order_id>' , methods=['POST','GET'])
def view_sale_detail(order_id):
    sale_detail = db.getCartItems(order_id)
    order_date = db.getOrderDate(order_id)
    return render_template('saleDetail.html', items=sale_detail, date=order_date)

@app.route('/viewInventory', methods=['POST','GET'])
def view_inventory():
    stock = db.getStockQuantity()
    products = db.getAllProducts()

    return render_template('inventory.html', stockList=stock, productsList=products)

@app.route('/setAlert', methods=['POST','GET'])
def set_alert():
    if request.method=='POST':
        product_id = request.form.get('product')
        qty = request.form.get('qty')
        db.setAlertQuantity(qty,product_id)
    return redirect(url_for('view_inventory'))



if __name__ == '__main__':
    app.run(debug=True)
