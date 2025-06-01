from pythonic.models import User, Lesson, Course, Task, Enrollment
from flask import render_template, url_for, flash, redirect, request, current_app
from pythonic.forms import RegistrationForm, LoginForm, UpdateProfileForm, ChangePasswordForm, DeleteAccountForm, CourseForm, LessonForm, RequestResetForm, ResetPasswordForm
from pythonic import app, db, mail
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
import os
import secrets
from datetime import datetime
from pythonic.utils import send_email
from urllib.parse import unquote


lessons = [
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
]

courses = [
    {
        "name": "Python",
        "icon": "python.svg",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Data Analysis",
        "icon": "analysis.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Machine Learning",
        "icon": "machine-learning.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Web Design",
        "icon": "web.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Blockchain",
        "icon": "blockchain.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Tips & Tricks",
        "icon": "idea.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
]


@app.route("/")
@app.route("/home")
def home():
    query = request.args.get('query', '').strip().lower()
    is_search = bool(query)
    
    # Get limited courses for performance
    db_courses = Course.query.order_by(Course.id.desc()).limit(12).all()
    
    # Convert database courses
    formatted_db_courses = [
        {
            "name": course.title,
            "icon": course.icon,
            "description": course.description
        }
        for course in db_courses
    ]
    
    # Combine courses
    all_courses = courses + formatted_db_courses
    
    # Filter if search query exists
    if query and len(query) >= 2:
        filtered_courses = [
            course for course in all_courses
            if (query in course['name'].lower() or 
                query in course['description'].lower())
        ]
        if not filtered_courses:
            flash(f'No courses found matching "{query}"', 'info')
            return redirect(url_for('home'))
        all_courses = filtered_courses
    
    # Get limited lessons for performance
    lessons = Lesson.query.order_by(Lesson.date_posted.desc()).limit(6).all()
    
    return render_template(
        "home.html", 
        lessons=lessons, 
        courses=all_courses,
        search_query=query,
        is_search=is_search
    )


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    # Check if user is admin
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Only administrators can create new accounts.', 'danger')
        return redirect(url_for('home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        if existing_email:
            flash('Email already exists. Please use a different one.', 'danger')
            return redirect(url_for('register'))
            
        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            fname=form.fname.data,
            lname=form.lname.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            image_file="default.jpg",  # Default profile picture
            is_admin=False  # New users are not admins by default
        )
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        flash(f"Account created successfully for {form.username.data}", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    # Save the file without resizing for now
    form_picture.save(picture_path)
    
    return picture_fn

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    password_form = ChangePasswordForm()
    delete_form = DeleteAccountForm()
    
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        # Check if username or email already exists (excluding current user)
        if form.username.data != current_user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'danger')
                return redirect(url_for('profile'))
        
        if form.email.data != current_user.email:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already exists. Please use a different one.', 'danger')
                return redirect(url_for('profile'))
        
        current_user.fname = form.fname.data
        current_user.lname = form.lname.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.fname.data = current_user.fname
        form.lname.data = current_user.lname
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('profile.html', title='Profile', 
                         form=form, password_form=password_form, 
                         delete_form=delete_form)

@app.route("/change-password", methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
    return redirect(url_for('profile'))

@app.route("/delete-account", methods=['POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        # Delete user's profile picture if it's not the default
        if current_user.image_file != 'default.jpg':
            picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
            if os.path.exists(picture_path):
                os.remove(picture_path)
        
        # Delete user's lessons
        Lesson.query.filter_by(user_id=current_user.id).delete()
        
        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('home'))
    return redirect(url_for('profile'))

@app.route("/course/<course_name>")
def course_details(course_name):
    # Decode the URL-encoded course name
    decoded_course_name = unquote(course_name)
    
    # First try to find the course in hardcoded courses
    hardcoded_course = next((c for c in courses if c["name"].lower() == decoded_course_name.lower()), None)
    
    if hardcoded_course:
        # If found in hardcoded courses, get related lessons from hardcoded list
        related_lessons = [lesson for lesson in lessons if lesson["course"].lower() == decoded_course_name.lower()]
        is_enrolled = False
        if current_user.is_authenticated:
            # For hardcoded courses, we'll just show the enrollment button
            is_enrolled = False
        
        return render_template(
            "course_details.html",
            title=f"{hardcoded_course['name']} Course",
            course=hardcoded_course,
            lessons=related_lessons,
            is_enrolled=is_enrolled
        )
    else:
        # If not found in hardcoded courses, try to find in database
        db_course = Course.query.filter_by(title=decoded_course_name).first()
        if db_course:
            is_enrolled = False
            if current_user.is_authenticated:
                enrollment = Enrollment.query.filter_by(
                    user_id=current_user.id,
                    course_id=db_course.id
                ).first()
                is_enrolled = enrollment is not None
            
            # Get lessons for this course
            db_lessons = Lesson.query.filter_by(course_id=db_course.id).all()
            
            return render_template(
                "course_details.html",
                title=f"{db_course.title} Course",
                course=db_course,
                lessons=db_lessons,
                is_enrolled=is_enrolled
            )
        else:
            flash("Course not found!", "danger")
            return redirect(url_for("home"))

@app.route("/database")
def view_database():
    # Get all data from database
    users = User.query.all()
    courses = Course.query.all()
    lessons = Lesson.query.all()
    
    return render_template(
        "database.html",
        title="Database Contents",
        users=users,
        courses=courses,
        lessons=lessons
    )

@app.route("/dashboard")
@login_required
def dashboard():
    courses = Course.query.all()
    lessons = Lesson.query.all()
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('dashboard.html', courses=courses, lessons=lessons, tasks=tasks)

@app.route("/search/courses")
def search_courses():
    query = request.args.get('query', '').strip().lower()
    
    if not query or len(query) < 2:
        flash('Please enter at least 2 characters to search', 'info')
        return redirect(url_for('home'))
    
    try:
        # Search in both hardcoded and database courses efficiently
        results = []
        
        # Search hardcoded courses
        for course in courses:
            if (query in course['name'].lower() or 
                query in course['description'].lower()):
                results.append(course)
        
        # Search database courses with proper indexing
        db_results = Course.query.filter(
            db.or_(
                Course.title.ilike(f'%{query}%'),
                Course.description.ilike(f'%{query}%')
            )
        ).limit(20).all()  # Limit results for performance
        
        # Format database results
        for course in db_results:
            results.append({
                "name": course.title,
                "icon": course.icon,
                "description": course.description
            })
        
        if not results:
            flash(f'No courses found matching "{query}"', 'info')
            return redirect(url_for('home'))
        
        # Get limited lessons for context
        lessons = Lesson.query.order_by(Lesson.date_posted.desc()).limit(6).all()
        
        return render_template(
            "home.html",
            courses=results,
            lessons=lessons,
            search_query=query,
            is_search=True
        )
        
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        flash('An error occurred while searching. Please try again.', 'danger')
        return redirect(url_for('home'))

@app.route("/dashboard/tasks", methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        
        if not title:
            flash('Task title is required', 'danger')
            return redirect(url_for('tasks'))
            
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
            task = Task(
                title=title,
                description=description,
                due_date=due_date,
                user_id=current_user.id
            )
            db.session.add(task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('tasks'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding task. Please try again.', 'danger')
            return redirect(url_for('tasks'))
    
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=tasks)

@app.route("/dashboard/tasks/<int:task_id>/update", methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
        
    status = request.form.get('status')
    if status in ['pending', 'in_progress', 'completed']:
        task.status = status
        db.session.commit()
        flash('Task status updated!', 'success')
    return redirect(url_for('tasks'))

@app.route("/dashboard/tasks/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
        
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks'))

@app.route("/dashboard/courses", methods=['GET'])
@login_required
def manage_courses():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    courses = Course.query.all()
    return render_template('courses/manage_courses.html', courses=courses)

@app.route("/dashboard/courses/create", methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            icon='default_course.png'  # Default icon
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('manage_courses'))
    return render_template('courses/course_form.html', form=form, course=None)

@app.route("/dashboard/courses/<int:course_id>/update", methods=['GET', 'POST'])
@login_required
def update_course(course_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    form = CourseForm()
    
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('manage_courses'))
    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
    
    return render_template('courses/course_form.html', form=form, course=course)

@app.route("/dashboard/courses/<int:course_id>/delete", methods=['POST'])
@login_required
def delete_course(course_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('manage_courses'))

@app.route("/dashboard/lessons", methods=['GET'])
@login_required
def manage_lessons():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    lessons = Lesson.query.all()
    return render_template('lessons/manage_lessons.html', lessons=lessons)

@app.route("/dashboard/lessons/create", methods=['GET', 'POST'])
@login_required
def create_lesson():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = LessonForm()
    # Populate course choices
    form.course_id.choices = [(c.id, c.title) for c in Course.query.all()]
    
    if form.validate_on_submit():
        lesson = Lesson(
            title=form.title.data,
            content=form.content.data,
            course_id=form.course_id.data,
            user_id=current_user.id,
            date_posted=datetime.utcnow()
        )
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('manage_lessons'))
    return render_template('lessons/lesson_form.html', form=form, lesson=None)

@app.route("/dashboard/lessons/<int:lesson_id>/update", methods=['GET', 'POST'])
@login_required
def update_lesson(lesson_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm()
    # Populate course choices
    form.course_id.choices = [(c.id, c.title) for c in Course.query.all()]
    
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.content = form.content.data
        lesson.course_id = form.course_id.data
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('manage_lessons'))
    elif request.method == 'GET':
        form.title.data = lesson.title
        form.content.data = lesson.content
        form.course_id.data = lesson.course_id
    
    return render_template('lessons/lesson_form.html', form=form, lesson=lesson)

@app.route("/dashboard/lessons/<int:lesson_id>/delete", methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('manage_lessons'))

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        db.session.commit()
        
        reset_url = url_for('reset_token', token=token, _external=True)
        send_email(
            subject='Password Reset Request',
            recipients=[user.email],
            text_body=f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.
''',
            html_body=f'''<p>To reset your password, visit the following link:</p>
<p><a href="{reset_url}">Reset Password</a></p>
<p>If you did not make this request then simply ignore this email and no changes will be made.</p>
'''
        )
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        user.reset_token = None
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/my-courses")
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