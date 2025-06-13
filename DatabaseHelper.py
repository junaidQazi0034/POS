from datetime import date
import mysql.connector

dbCon = mysql.connector.connect(host="localhost", user="root", password="", database="db_pos")
cursor = dbCon.cursor()

###------------- User management functions --------------------###

def registeruser(name, username, password, gender, age,userType):
    query ="INSERT INTO users(name, username, password, gender, age, userType) VALUES(%s, %s,%s,%s,%s,%s)"
    values = [name,username,password,gender,age,userType]
    cursor.execute(query, values)
    dbCon.commit()

def loginUser(username, password, userType):
    query ="select * from users where username=%s and password=%s and userType=%s"
    queryParameters =[username, password,userType]
    cursor.execute(query, queryParameters)
    userData = cursor.fetchone()
    if userData:
        # messagebox.showinfo("Success", "Welcome you are Logged in successfully")
        return True
    else:
        # messagebox.showerror("Login Failed", "Username or password is invalid")   
        return False

def loginAdmin(username, password):
    query ="select * from admin where username=%s and password=%s"
    queryParameters =[username, password]
    cursor.execute(query, queryParameters)
    userData = cursor.fetchone()
    if userData:
        return True
    else:
        return False

def updateUser(name, username, password, gender, age,userType, uid):
    query ="UPDATE users SET name=%s, username=%s, password=%s, gender=%s, age=%s, userType=%s WHERE userid=%s"
    values = [name,username,password,gender,age,userType, uid]
    cursor.execute(query, values)
    dbCon.commit()

def deleteUser(userid):
    query ="DELETE from users WHERE userid=%s"
    values = [userid]
    cursor.execute(query, values)
    dbCon.commit()

def getUserData(userid):
    query ="select * from users where  userid=%s"
    queryParameters =[userid]
    cursor.execute(query, queryParameters)
    userData = cursor.fetchone()
    return userData

def getAllUsers():
    query ="select * from users order by name"
    cursor.execute(query)
    userslist = cursor.fetchall()
    return userslist
     
###------------- Product management functions --------------------###
def addProduct(name, size,  category, unitPrice):
    query ="INSERT INTO products(name, size,  category, unitPrice) VALUES(%s, %s,%s,%s)"
    values = [name, size,  category, unitPrice]
    cursor.execute(query, values)
    dbCon.commit()

def updateProduct(name, size,  category, unitPrice, productId):
    query ="UPDATE products SET name=%s, size=%s, category=%s, unitPrice=%s WHERE id=%s"
    values = [name, size,  category, unitPrice, productId]
    cursor.execute(query, values)
    dbCon.commit()

def deleteProduct(productID):
    query ="DELETE from products WHERE id=%s"
    values = [productID]
    cursor.execute(query, values)
    dbCon.commit()

def getproduct(productID):
    query ="select * from products where  id=%s"
    queryParameters =[productID]
    cursor.execute(query, queryParameters)
    productData = cursor.fetchone()
    return productData

def getAllProducts():
    query ="select * from products order by name"
    cursor.execute(query)
    productlist = cursor.fetchall()
    return productlist
   
###------------- cart management functions --------------------###
def add2Cart(product_id, qty, order_id):
    query ="INSERT INTO cart(product_id, qty, order_id) VALUES(%s, %s,%s)"
    values = [product_id, qty, order_id]
    cursor.execute(query, values)
    dbCon.commit()

def updateCart(cart_id, qty):
    query ="UPDATE cart SET qty=%s WHERE id=%s"
    values = [qty, cart_id]
    cursor.execute(query, values)
    dbCon.commit()

def deleteCartItem(cartID):
    query ="DELETE from cart WHERE id=%s"
    values = [cartID]
    cursor.execute(query, values)
    dbCon.commit()

def getCartItems(order_id):
    query = "SELECT cart.id as cart_id, products.name, products.unitprice, cart.qty FROM cart JOIN products ON cart.product_id = products.id WHERE cart.order_id=%s"
    cursor.execute(query,[order_id])
    list = cursor.fetchall()
    return list

def getAllOrders():
    query ="select count(*) as items, order_id from cart group by order_id order by order_id DESC"
    cursor.execute(query)
    ordersList = cursor.fetchall()
    return ordersList

def countCartItems():
    query ="select count(*) as items, order_id from cart where completed=0 group by order_id order by order_id DESC "
    cursor.execute(query)
    itemCount = cursor.fetchone()
    return itemCount 

def updateCartCompletion(order_id):
    query ="UPDATE cart SET completed=1 WHERE order_id=%s"
    values = [order_id]
    cursor.execute(query, values)
    dbCon.commit() 

###------------- sales and inventory management functions --------------------###
def newOrder():
    query = "insert into orders(order_date) values(%s)"
    vals = [date.today()]
    cursor.execute(query, vals)
    dbCon.commit()

def getLastOrderID():
    query = "select max(id) as order_id from orders"
    cursor.execute(query)
    order_id = cursor.fetchone()[0]
    return order_id

def getAllSales():
    query="select order_id, count(*) as qty,  order_date from cart inner join orders on orders.id=cart.order_id where completed=1 group by order_id"
    cursor.execute(query)
    salesList = cursor.fetchall()
    return salesList

def getOrderDate(order_id):
    query="select order_date from orders where id=%s"
    vals=[order_id]
    cursor.execute(query,vals)
    date = cursor.fetchone()[0]
    return date

def debitStock(order_id):  #--- decrementing the stock on sales ----#
    query = "insert into stock(product_id, order_id, qty, transaction_type) SELECT product_id,order_id, -qty,'Sale' FROM cart where order_id=%s"
    values = [order_id]
    cursor.execute(query, values)
    dbCon.commit() 

def creditStock(product_id, qty):   #--- incrementing the stock on purchase ----#
    query = "insert into stock(product_id, qty, transaction_type) VALUES(%s,%s,%s)"
    values = [product_id, qty,  "Purchase"]
    cursor.execute(query, values)
    dbCon.commit() 

def getStockQuantity():
    # query="select name,size,category, sum(qty) as quantity from products inner join stock on products.id=stock.product_id group by name, size, category"
    query = "select product_id,name,size,category,sum(qty)as stockQty, (sum(qty)-alertqty) as alertQuantity from stock inner join products on products.id=stock.product_id group by product_id,name,size,category ORDER BY alertQuantity"
    cursor.execute(query)
    productsList = cursor.fetchall()
    return productsList

def setAlertQuantity(alertQty,product_id):
    query ="update products set alertQty=%s Where id=%s"
    vals = [alertQty,product_id]
    cursor.execute(query, vals)
    dbCon.commit()

