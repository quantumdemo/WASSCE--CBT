import os
from flask import Flask
from dotenv import load_dotenv

# Import extensions from the new file
from app.extensions import db, migrate, login_manager, mail

load_dotenv()

def create_app(config_class=None):
    app = Flask(__name__)

    # Load configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_secret_key')
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, '..', 'site.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email configuration for production SMTP
    # These values are loaded from the .env file.
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') # e.g., 'smtp.gmail.com'
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587)) # Port for TLS
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1'] # Use Transport Layer Security
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') # Your email address
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') # Your email password or app-specific password
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER') # The "From" address for emails

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Import models inside create_app to avoid circular imports with extensions
    with app.app_context():
        from app import models

    # Register CLI commands
    from app import commands
    commands.register_commands(app)

    return app