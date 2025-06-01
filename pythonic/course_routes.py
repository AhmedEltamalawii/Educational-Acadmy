from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from pythonic.models import Course, Lesson, Enrollment
from pythonic import db
from flask_login import login_required, current_user
from pythonic.forms import CourseForm
import os
import secrets
from urllib.parse import unquote

courses = Blueprint('courses', __name__)

def save_course_icon(icon_file):
    # Generate a random filename to avoid conflicts
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(icon_file.filename)
    icon_filename = random_hex + file_ext
    
    # Ensure the upload directory exists
    upload_dir = os.path.join(current_app.root_path, 'static', 'course_icons')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    icon_path = os.path.join(upload_dir, icon_filename)
    icon_file.save(icon_path)
    
    return icon_filename

@courses.route('/courses')
def list_courses():
    courses = Course.query.all()
    return render_template('courses/all_courses.html', courses=courses)

@courses.route('/course/<int:course_id>')
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).all()
    return render_template('course_details.html', course=course, lessons=lessons)

@courses.route('/course/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    form = CourseForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        
        # Handle icon upload
        icon_filename = 'default_icon.jpg'
        if form.icon.data:
            try:
                icon_filename = save_course_icon(form.icon.data)
            except Exception as e:
                flash('Error uploading icon. Please try again.', 'danger')
                return render_template('courses/create_course.html', form=form)
        
        course = Course(
            title=title,
            description=description,
            icon=icon_filename
        )
        
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('courses.list_courses'))
    
    return render_template('courses/create_course.html', form=form)

@courses.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
@login_required
def update_course(course_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.icon = request.form.get('icon', course.icon)
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('courses.list_courses'))
    
    return render_template('courses/update_course.html', course=course)

@courses.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    course = Course.query.get_or_404(course_id)
    
    # Delete associated lessons first
    Lesson.query.filter_by(course_id=course_id).delete()
    
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses.list_courses'))

@courses.route("/course/<course_name>")
def course_details(course_name):
    # Decode the URL-encoded course name
    decoded_course_name = unquote(course_name)
    course = Course.query.filter_by(title=decoded_course_name).first_or_404()
    
    is_enrolled = False
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        is_enrolled = enrollment is not None
    
    # Get lessons for this course
    lessons = Lesson.query.filter_by(course_id=course.id).all()
    
    return render_template(
        "course_details.html",
        title=f"{course.title} Course",
        course=course,
        lessons=lessons,
        is_enrolled=is_enrolled
    )

@courses.route("/course/<int:course_id>/enroll", methods=['POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course!', 'info')
        return redirect(url_for('courses.course_details', course_name=course.title))
    
    # Create new enrollment
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Successfully enrolled in {course.title}!', 'success')
    return redirect(url_for('courses.course_details', course_name=course.title))

@courses.route("/course/<int:course_id>/unenroll", methods=['POST'])
@login_required
def unenroll_course(course_id):
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first_or_404()
    
    course = Course.query.get(course_id)
    
    db.session.delete(enrollment)
    db.session.commit()
    
    flash(f'Successfully unenrolled from {course.title}', 'success')
    return redirect(url_for('courses.course_details', course_name=course.title))

@courses.route("/my-courses")
@login_required
def my_courses():
    # Get all active enrollments for the current user
    enrollments = Enrollment.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).all()
    
    # Get the course objects from enrollments
    enrolled_courses = []
    for enrollment in enrollments:
        course = Course.query.get(enrollment.course_id)
        if course:
            enrolled_courses.append(course)
    
    return render_template(
        "my_courses.html",
        title="My Courses",
        enrolled_courses=enrolled_courses
    ) 