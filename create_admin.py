from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    if not User.query.filter_by(email="admin@gmail.com").first():
        admin = User(
            username="admin",
            email="admin@gmail.com",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created")
    else:
        print("⚠ Admin already exists")
