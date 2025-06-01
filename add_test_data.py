from pythonic import app, db
from pythonic.models import User, Course, Lesson
from datetime import datetime
from werkzeug.security import generate_password_hash

def add_test_data():
    with app.app_context():
        # Clear existing data
        User.query.delete()
        Course.query.delete()
        Lesson.query.delete()
        
        # Add users
        user1 = User(
            fname="John",
            lname="Doe",
            username="johndoe",
            email="john@example.com",
            password=generate_password_hash("password123"),
            image_file="default.jpg"
        )
        
        user2 = User(
            fname="Jane",
            lname="Smith",
            username="janesmith",
            email="jane@example.com",
            password=generate_password_hash("password123"),
            image_file="default.jpg"
        )
        
        db.session.add(user1)
        db.session.add(user2)
        
        # Add courses
        course1 = Course(
            title="Python Programming",
            description="Learn Python from scratch",
            icon="python_icon.jpg"
        )
        
        course2 = Course(
            title="Web Development",
            description="Build modern web applications",
            icon="web_icon.jpg"
        )
        
        db.session.add(course1)
        db.session.add(course2)
        
        # Commit to get IDs
        db.session.commit()
        
        # Add lessons
        lesson1 = Lesson(
            title="Introduction to Python",
            content="Python is a high-level programming language...",
            thumbnail="python_thumb.jpg",
            slug="intro-python",
            user_id=user1.id,
            course_id=course1.id,
            date_posted=datetime.utcnow()
        )
        
        lesson2 = Lesson(
            title="Python Data Types",
            content="Python has several built-in data types...",
            thumbnail="python_thumb.jpg",
            slug="python-data-types",
            user_id=user1.id,
            course_id=course1.id,
            date_posted=datetime.utcnow()
        )
        
        lesson3 = Lesson(
            title="HTML Basics",
            content="HTML is the standard markup language...",
            thumbnail="web_thumb.jpg",
            slug="html-basics",
            user_id=user2.id,
            course_id=course2.id,
            date_posted=datetime.utcnow()
        )
        
        db.session.add(lesson1)
        db.session.add(lesson2)
        db.session.add(lesson3)
        
        # Final commit
        db.session.commit()
        print("Test data added successfully!")

if __name__ == "__main__":
    add_test_data() 