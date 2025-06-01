from pythonic import app, db
from pythonic.models import User, Course, Lesson

with app.app_context():
    # Get all users
    users = User.query.all()
    print("\n=== Users ===")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

    # Get all courses
    courses = Course.query.all()
    print("\n=== Courses ===")
    for course in courses:
        print(f"ID: {course.id}, Title: {course.title}, Description: {course.description}")

    # Get all lessons
    lessons = Lesson.query.all()
    print("\n=== Lessons ===")
    for lesson in lessons:
        print(f"ID: {lesson.id}, Title: {lesson.title}, Course ID: {lesson.course_id}") 