from flask import Flask, render_template
from database import create_tables

from flask import Flask, render_template, request, redirect, flash, session

from datetime import datetime


from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection, create_tables



app = Flask(__name__)
app.secret_key = "localstore_secret_key_123"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    conn = get_connection()
    cursor = conn.cursor()

    if search:
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            ("%" + search + "%",)
        )
    else:
        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()
    conn.close()

    return render_template(
        "products.html",
        products=products,
        search=search
    )


@app.route("/cart")
def cart():

    cart = session.get("cart", [])

    conn = get_connection()
    cursor = conn.cursor()

    products = []
    total = 0

    for product_id in cart:
        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()

        if product:
            products.append(product)
            total += product["price"]

    conn.close()

    return render_template(
        "cart.html",
        products=products,
        total=total
    )

@app.route("/checkout")
def checkout():

    if "user_id" not in session:
        return redirect("/login")

    if "cart" not in session or len(session["cart"]) == 0:
        flash("Your cart is empty!")
        return redirect("/cart")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO orders(user_id, order_date) VALUES(?, ?)",
        (session["user_id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    order_id = cursor.lastrowid

    for product_id in session["cart"]:
        cursor.execute(
            "INSERT INTO order_items(order_id, product_id) VALUES(?, ?)",
            (order_id, product_id)
        )

    conn.commit()
    conn.close()

    session["cart"] = []

    flash("🎉 Order placed successfully!")
    return render_template("checkout.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        conn.close()
        
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            flash("Login Successful!")
            return redirect("/")
        
        
        
        flash("Invalid Email or Password")

    return render_template("login.html")

@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM orders
        WHERE user_id=?
        ORDER BY id DESC
    """, (session["user_id"],))

    orders = cursor.fetchall()

    conn.close()

    return render_template("orders.html", orders=orders)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/admin")
def admin():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    orders = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        users=users,
        products=products,
        orders=orders
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        flash("Registration Successful!")
        return redirect("/login")

    return render_template("register.html")

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    cart.append(product_id)
    session["cart"] = cart

    flash("Product added to cart!")
    return redirect("/products")

@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", [])

    if product_id in cart:
        cart.remove(product_id)

    session["cart"] = cart

    flash("Product removed from cart!")
    return redirect("/cart")

if __name__ == "__main__":
    create_tables()
    app.run()
    
