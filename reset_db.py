from pythonic import app, db
from pythonic.models import User, Course, Lesson
from werkzeug.security import generate_password_hash

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped.")
        
        # Create all tables
        db.create_all()
        print("All tables created.")
        
        # Create admin user
        admin = User(
            fname="Admin",
            lname="User",
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("Admin@123"),
            image_file="default.jpg",
            is_admin=True,
            reset_token=None
        )
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")

if __name__ == "__main__":
    reset_database() 