from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from pythonic.models import Lesson, Course
from pythonic import db
from flask_login import login_required, current_user
from datetime import datetime
import secrets
import os

lessons = Blueprint('lessons', __name__)

def save_lesson_thumbnail(thumbnail_file):
    # Generate a random filename to avoid conflicts
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(thumbnail_file.filename)
    thumbnail_filename = random_hex + file_ext
    
    # Ensure the upload directory exists
    upload_dir = os.path.join(current_app.root_path, 'static', 'lesson_thumbnails')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    thumbnail_path = os.path.join(upload_dir, thumbnail_filename)
    thumbnail_file.save(thumbnail_path)
    
    return thumbnail_filename

@lessons.route('/lessons')
def list_lessons():
    lessons = Lesson.query.all()
    return render_template('lessons/all_lessons.html', lessons=lessons)

@lessons.route('/lesson/<int:lesson_id>')
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('lesson_details.html', lesson=lesson)

@lessons.route('/lesson/create', methods=['GET', 'POST'])
@login_required
def create_lesson():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        course_id = request.form.get('course_id')
        thumbnail = request.files.get('thumbnail')
        
        # Generate slug from title
        slug = secrets.token_hex(8)
        
        # Handle thumbnail upload
        thumbnail_filename = 'default_thumbnail.jpg'
        if thumbnail:
            try:
                thumbnail_filename = save_lesson_thumbnail(thumbnail)
            except Exception as e:
                flash('Error uploading thumbnail. Please try again.', 'danger')
                return render_template('lessons/create_lesson.html', courses=Course.query.all())
        
        lesson = Lesson(
            title=title,
            content=content,
            course_id=course_id,
            user_id=current_user.id,
            thumbnail=thumbnail_filename,
            slug=slug,
            date_posted=datetime.utcnow()
        )
        
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('lessons.list_lessons'))
    
    courses = Course.query.all()
    return render_template('lessons/create_lesson.html', courses=courses)

@lessons.route('/lesson/<int:lesson_id>/update', methods=['GET', 'POST'])
@login_required
def update_lesson(lesson_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if request.method == 'POST':
        lesson.title = request.form.get('title')
        lesson.content = request.form.get('content')
        lesson.course_id = request.form.get('course_id')
        
        thumbnail = request.files.get('thumbnail')
        if thumbnail:
            try:
                # Delete old thumbnail if it's not the default
                if lesson.thumbnail != 'default_thumbnail.jpg':
                    old_thumbnail_path = os.path.join(current_app.root_path, 'static', 'lesson_thumbnails', lesson.thumbnail)
                    if os.path.exists(old_thumbnail_path):
                        os.remove(old_thumbnail_path)
                
                # Save new thumbnail
                lesson.thumbnail = save_lesson_thumbnail(thumbnail)
            except Exception as e:
                flash('Error updating thumbnail. Please try again.', 'danger')
                return render_template('lessons/update_lesson.html', lesson=lesson, courses=Course.query.all())
        
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('lessons.list_lessons'))
    
    courses = Course.query.all()
    return render_template('lessons/update_lesson.html', lesson=lesson, courses=courses)

@lessons.route('/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Delete thumbnail if it's not the default
    if lesson.thumbnail != 'default_thumbnail.jpg':
        thumbnail_path = os.path.join(current_app.root_path, 'static', 'lesson_thumbnails', lesson.thumbnail)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
    
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('lessons.list_lessons')) 