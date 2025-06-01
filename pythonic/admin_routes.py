from flask import Blueprint, render_template, redirect, url_for, flash, request
from pythonic.models import User
from pythonic import db
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from pythonic.utils import send_admin_notification

admin = Blueprint('admin', __name__)

@admin.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Get form data
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.create_user'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.create_user'))
        
        # Create new user
        user = User(
            fname=fname,
            lname=lname,
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=is_admin
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send notification to admins
        send_admin_notification(
            subject='New User Created',
            message=f'A new user has been created:\nUsername: {username}\nEmail: {email}\nAdmin: {is_admin}'
        )
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/create_user.html')

@admin.route('/admin/users/<int:user_id>/update', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get form data
        user.fname = request.form.get('fname')
        user.lname = request.form.get('lname')
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.is_admin = 'is_admin' in request.form
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            user.password = generate_password_hash(new_password)
        
        db.session.commit()
        
        # Send notification to admins
        send_admin_notification(
            subject='User Updated',
            message=f'User has been updated:\nUsername: {user.username}\nEmail: {user.email}\nAdmin: {user.is_admin}'
        )
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/update_user.html', user=user)

@admin.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Send notification to admins before deletion
    send_admin_notification(
        subject='User Deleted',
        message=f'User has been deleted:\nUsername: {user.username}\nEmail: {user.email}'
    )
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users')) 