import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User, UserRole, School

def register_commands(app):
    @app.cli.command("create-admin")
    @click.argument("email")
    @click.argument("password")
    def create_admin(email, password):
        """Creates a new admin user."""
        if User.query.filter_by(email=email).first():
            print(f"Error: User with email {email} already exists.")
            return

        # Get or create a default school/centre for the admin
        school = School.query.filter_by(name='Default Centre').first()
        if not school:
            school = School(name='Default Centre')
            db.session.add(school)

        admin = User(
            email=email,
            full_name="Default Admin",
            role=UserRole.ADMIN,
            school=school,
            is_verified=True
        )
        admin.set_password(password)
        db.session.add(admin)

        # In a real setup, we would not have this issue.
        # For the sandbox, we must assume the commit works.
        try:
            db.session.commit()
            print(f"Admin user {email} created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create admin user. Error: {e}")
            print("NOTE: This may be due to the sandbox environment's database limitations.")

    app.cli.add_command(create_admin)