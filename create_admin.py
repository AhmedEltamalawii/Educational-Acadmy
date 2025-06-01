from pythonic import app, db
from pythonic.models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email="admin@example.com").first()
        if admin:
            print("Admin user already exists!")
            return

        # Create admin user
        admin = User(
            fname="Admin",
            lname="User",
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("Admin@123"),
            image_file="default.jpg",
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")

if __name__ == "__main__":
    create_admin() 