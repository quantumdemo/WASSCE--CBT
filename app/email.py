from flask_mail import Message
from app.extensions import mail
from flask import current_app

def send_email(to, subject, template):
    """
    A simple email sending utility.
    """
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    # In a real production environment, you might want to send this asynchronously.
    # With MAIL_SUPPRESS_SEND = True, this will run without error but no email will be sent.
    mail.send(msg)