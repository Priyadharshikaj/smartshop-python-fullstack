from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from . import db
from .models import User, Product, Order, OrderItem

main = Blueprint("main", __name__)

def current_user():
    user_id = session.get("user_id")
    return User.query.get(user_id) if user_id else None

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user.is_admin:
            flash("Admin access required.", "error")
            return redirect(url_for("main.index"))
        return fn(*args, **kwargs)
    return wrapper

def cart_details():
    raw_cart = session.get("cart", {})
    items = []
    total = 0

    for pid, qty in raw_cart.items():
        product = Product.query.get(int(pid))
        if product:
            qty = max(1, int(qty))
            subtotal = product.price * qty
            items.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": qty,
                "subtotal": subtotal,
                "image_url": product.image_url
            })
            total += subtotal

    return items, total

@main.context_processor
def inject_globals():
    items, total = cart_details()
    return {
        "current_user": current_user(),
        "cart_count": sum(item["quantity"] for item in items),
        "cart_total": total
    }

@main.route("/")
def index():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter_by(category=category)

    products = query.order_by(Product.id.desc()).all()
    categories = [row[0] for row in db.session.query(Product.category).distinct().all()]

    return render_template("index.html", products=products, categories=categories,
                           search=search, selected_category=category)

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 6:
            flash("Enter all details. Password must contain at least 6 characters.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("register.html")

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash(f"Welcome, {user.name}!", "success")
            return redirect(url_for("main.index"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")

@main.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))

@main.route("/cart")
def cart():
    items, total = cart_details()
    return render_template("cart.html", items=items, total=total)

@main.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash("This product is out of stock.", "error")
        return redirect(url_for("main.index"))

    cart = session.get("cart", {})
    key = str(product_id)
    new_qty = int(cart.get(key, 0)) + 1

    if new_qty > product.stock:
        flash("You cannot add more than available stock.", "error")
    else:
        cart[key] = new_qty
        session["cart"] = cart
        flash(f"{product.name} added to cart.", "success")

    return redirect(request.referrer or url_for("main.index"))

@main.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        qty = int(request.form.get("quantity", 1))
    except ValueError:
        qty = 1

    cart = session.get("cart", {})
    key = str(product_id)

    if qty <= 0:
        cart.pop(key, None)
    elif qty <= product.stock:
        cart[key] = qty
    else:
        flash(f"Only {product.stock} units are available.", "error")

    session["cart"] = cart
    return redirect(url_for("main.cart"))

@main.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("main.cart"))

@main.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not current_user():
        flash("Please login before checkout.", "error")
        return redirect(url_for("main.login"))

    items, total = cart_details()
    if not items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("main.cart"))

    if request.method == "POST":
        for item in items:
            product = Product.query.get(item["id"])
            if not product or item["quantity"] > product.stock:
                flash("Stock changed. Please review your cart.", "error")
                return redirect(url_for("main.cart"))

        order = Order(
            user_id=current_user().id,
            total=total,
            payment_method="Cash on Delivery"
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            product = Product.query.get(item["id"])
            product.stock -= item["quantity"]
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=item["quantity"]
            ))

        session["cart"] = {}
        db.session.commit()
        flash(f"Order #{order.id} placed successfully!", "success")
        return redirect(url_for("main.orders"))

    return render_template("checkout.html", items=items, total=total)

@main.route("/orders")
def orders():
    if not current_user():
        flash("Please login to view your orders.", "error")
        return redirect(url_for("main.login"))

    user_orders = Order.query.filter_by(user_id=current_user().id).order_by(
        Order.created_at.desc()
    ).all()
    return render_template("orders.html", orders=user_orders)

@main.route("/admin")
@admin_required
def admin():
    products = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template("admin.html", products=products, orders=orders)

@main.route("/admin/products/add", methods=["POST"])
@admin_required
def admin_add_product():
    try:
        product = Product(
            name=request.form["name"].strip(),
            category=request.form["category"].strip(),
            price=float(request.form["price"]),
            stock=int(request.form["stock"]),
            description=request.form["description"].strip(),
            image_url=request.form["image_url"].strip()
        )
        if product.price < 0 or product.stock < 0:
            raise ValueError
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully.", "success")
    except (KeyError, ValueError):
        flash("Please enter valid product details.", "error")

    return redirect(url_for("main.admin"))

@main.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("main.admin"))

# ---------------- REST API ----------------

def product_json(product):
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "stock": product.stock,
        "description": product.description,
        "image_url": product.image_url
    }

@main.route("/api/products")
def api_products():
    products = Product.query.order_by(Product.id.desc()).all()
    return jsonify([product_json(p) for p in products])

@main.route("/api/products/<int:product_id>")
def api_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product_json(product))

@main.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or len(password) < 6:
        return jsonify({"error": "Invalid registration data"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered", "user_id": user.id}), 201

@main.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Login successful", "user_id": user.id})

@main.route("/api/cart", methods=["GET"])
def api_cart():
    if not current_user():
        return jsonify({"error": "Login required"}), 401
    items, total = cart_details()
    return jsonify({"items": items, "total": total})

@main.route("/api/cart", methods=["POST"])
def api_add_cart():
    if not current_user():
        return jsonify({"error": "Login required"}), 401

    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    product = Product.query.get(product_id)
    if not product or quantity < 1 or quantity > product.stock:
        return jsonify({"error": "Invalid product or quantity"}), 400

    cart = session.get("cart", {})
    cart[str(product.id)] = quantity
    session["cart"] = cart
    return jsonify({"message": "Cart updated"})

@main.route("/api/cart/<int:product_id>", methods=["PUT", "DELETE"])
def api_update_cart(product_id):
    if not current_user():
        return jsonify({"error": "Login required"}), 401

    cart = session.get("cart", {})
    key = str(product_id)

    if request.method == "DELETE":
        cart.pop(key, None)
    else:
        data = request.get_json(silent=True) or {}
        quantity = int(data.get("quantity", 1))
        product = Product.query.get(product_id)
        if not product or quantity < 1 or quantity > product.stock:
            return jsonify({"error": "Invalid quantity"}), 400
        cart[key] = quantity

    session["cart"] = cart
    return jsonify({"message": "Cart updated"})

@main.route("/api/checkout", methods=["POST"])
def api_checkout():
    if not current_user():
        return jsonify({"error": "Login required"}), 401

    items, total = cart_details()
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    for item in items:
        product = Product.query.get(item["id"])
        if not product or item["quantity"] > product.stock:
            return jsonify({"error": "Insufficient stock"}), 400

    order = Order(
        user_id=current_user().id,
        total=total,
        payment_method="Cash on Delivery"
    )
    db.session.add(order)
    db.session.flush()

    for item in items:
        product = Product.query.get(item["id"])
        product.stock -= item["quantity"]
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=item["quantity"]
        ))

    session["cart"] = {}
    db.session.commit()

    return jsonify({
        "message": "Order placed",
        "order_id": order.id,
        "total": total
    }), 201

@main.route("/api/orders")
def api_orders():
    if not current_user():
        return jsonify({"error": "Login required"}), 401

    result = []
    for order in Order.query.filter_by(user_id=current_user().id).order_by(
        Order.created_at.desc()
    ).all():
        result.append({
            "id": order.id,
            "total": order.total,
            "status": order.status,
            "payment_method": order.payment_method,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "product_name": item.product_name,
                    "price": item.price,
                    "quantity": item.quantity
                } for item in order.items
            ]
        })
    return jsonify(result)
