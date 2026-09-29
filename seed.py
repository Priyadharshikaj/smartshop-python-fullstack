from app import create_app, db
from app.models import User, Product

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@smartshop.com").first():
        db.session.add(User(
            name="Admin",
            email="admin@smartshop.com",
            password="admin123",
            is_admin=True
        ))

    if not User.query.filter_by(email="demo@gmail.com").first():
        db.session.add(User(
            name="Demo User",
            email="demo@gmail.com",
            password="demo123",
            is_admin=False
        ))

    if Product.query.count() == 0:
        products = [
            Product(name="Wireless Headphones", category="Electronics",
                    price=1499, stock=20,
                    description="Comfortable Bluetooth headphones with clear sound.",
                    image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"),
            Product(name="Smart Watch", category="Electronics",
                    price=2299, stock=15,
                    description="Fitness tracking smart watch with notifications.",
                    image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"),
            Product(name="Laptop Backpack", category="Accessories",
                    price=999, stock=30,
                    description="Water-resistant backpack suitable for laptops and travel.",
                    image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"),
            Product(name="Running Shoes", category="Fashion",
                    price=1799, stock=18,
                    description="Lightweight running shoes designed for daily comfort.",
                    image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"),
            Product(name="Cotton T-Shirt", category="Fashion",
                    price=699, stock=40,
                    description="Soft cotton regular-fit t-shirt for everyday wear.",
                    image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800"),
            Product(name="Coffee Mug", category="Home",
                    price=349, stock=50,
                    description="Minimal ceramic mug for coffee and tea.",
                    image_url="https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=800"),
            Product(name="Desk Lamp", category="Home",
                    price=899, stock=25,
                    description="Modern LED desk lamp for study and work.",
                    image_url="https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800"),
            Product(name="Bluetooth Speaker", category="Electronics",
                    price=1299, stock=22,
                    description="Portable Bluetooth speaker with powerful audio.",
                    image_url="https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800"),
        ]
        db.session.add_all(products)

    db.session.commit()
    print("Database ready. Demo users and products have been created.")
