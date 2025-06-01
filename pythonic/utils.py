from flask import current_app
from flask_mail import Message
from pythonic import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_admin_notification(subject, message):
    """Send notification to admin users"""
    from pythonic.models import User
    admin_users = User.query.filter_by(is_admin=True).all()
    admin_emails = [admin.email for admin in admin_users]
    
    if admin_emails:
        send_email(
            subject=subject,
            recipients=admin_emails,
            text_body=message,
            html_body=f'<p>{message}</p>'
        ) 