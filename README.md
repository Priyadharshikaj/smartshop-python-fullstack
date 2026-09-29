# SmartShop - Python Full Stack E-Commerce Project

A beginner-friendly full-stack e-commerce project built with:

- Python Flask
- SQLAlchemy ORM
- SQLite by default (easy to run)
- MySQL-ready database configuration
- HTML5
- CSS3
- JavaScript
- REST API
- Session-based authentication
- Product search/filter
- Shopping cart
- Checkout and order history
- Admin product management

## 1. Project structure

```text
Python_Full_Stack_Ecommerce_Project/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── cart.html
│   │   ├── checkout.html
│   │   ├── orders.html
│   │   └── admin.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
│
├── run.py
├── seed.py
├── requirements.txt
└── README.md
```

## 2. Requirements

Install Python 3.10 or newer.

Check:

```bat
python --version
```

## 3. Installation on Windows

Open Command Prompt in this project folder.

Create a virtual environment:

```bat
python -m venv venv
```

Activate it:

```bat
venv\Scripts\activate
```

Install packages:

```bat
pip install -r requirements.txt
```

## 4. Create sample products

Run:

```bat
python seed.py
```

This creates the database and sample products.

## 5. Start the project

Run:

```bat
python run.py
```

Open:

http://127.0.0.1:5000

## 6. Demo accounts

Customer:
- Email: demo@gmail.com
- Password: demo123

Admin:
- Email: admin@smartshop.com
- Password: admin123

The admin can add and delete products.

## 7. MySQL option

The project uses SQLite by default so that you can run it without MySQL configuration.

If your institute requires MySQL, create a database:

```sql
CREATE DATABASE smartshop;
```

Then set the environment variable before running:

```bat
set DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/smartshop
```

Install the MySQL driver:

```bat
pip install pymysql
```

Then:

```bat
python seed.py
python run.py
```

If your MySQL password contains characters such as `@`, URL-encoding may be required. For example, `@` becomes `%40`.

## 8. Main features

1. User registration
2. User login/logout
3. Product listing
4. Search products
5. Category filter
6. Product details
7. Add to cart
8. Update/remove cart items
9. Checkout
10. Order history
11. REST API
12. Admin dashboard
13. Add/delete products
14. Responsive UI

## 9. API endpoints

- GET `/api/products`
- GET `/api/products/<id>`
- POST `/api/register`
- POST `/api/login`
- GET `/api/cart`
- POST `/api/cart`
- PUT `/api/cart/<product_id>`
- DELETE `/api/cart/<product_id>`
- POST `/api/checkout`
- GET `/api/orders`

## 10. Suggested demo flow

1. Explain the problem: small online shops need a simple digital storefront.
2. Show the home page.
3. Search for a product.
4. Register/login.
5. Add products to cart.
6. Change quantity.
7. Checkout.
8. Open order history.
9. Logout.
10. Login as admin.
11. Add a product.
12. Delete a product.
13. Explain the database and API.
14. Show the project folder and code.

## 11. Technologies to mention in your viva

Frontend:
- HTML
- CSS
- JavaScript

Backend:
- Python
- Flask

Database:
- SQLite / MySQL
- SQLAlchemy ORM

API:
- REST API
- JSON

Security:
- Password hashing
- Session authentication
- Server-side validation

## 12. Important note

This is an educational project. It does not connect to a real payment gateway. Checkout records an order in the database and uses a demo "Cash on Delivery" payment method.
