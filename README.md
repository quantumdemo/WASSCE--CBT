# WASSCE CBT Practice Platform

This project is a comprehensive Computer-Based Testing (CBT) platform designed for students preparing for the West African Senior School Certificate Examination (WASSCE). It provides a feature-rich environment for students, teachers, and administrators.

## Features

*   **Student Role:** Register and log in, take practice and mock exams, view exam history and performance analytics.
*   **Teacher Role:** Manage a question bank, build custom exams, grade subjective questions, and view student analytics.
*   **Admin Role:** Manage all users and learning centres, and configure global system settings.
*   **Dynamic Exam Interface:** Includes a countdown timer, question navigation, "mark-for-review" functionality, and auto-saving of answers.
*   **Advanced Authentication:** Secure user authentication with email (OTP) verification and a "Forgot Password" flow.

## Tech Stack

*   **Backend:** Python (Flask)
*   **Database:** SQLAlchemy ORM, Flask-Migrate for migrations.
    *   **Development:** SQLite
    *   **Production:** PostgreSQL
*   **Frontend:** Plain HTML, CSS, and JavaScript (no frameworks).
*   **Email:** Flask-Mail for sending transactional emails.

---

## Setup and Installation

Follow these steps to set up the project locally.

### 1. Prerequisites

*   Python 3.8+
*   A virtual environment tool (e.g., `venv`)

### 2. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 3. Set Up a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS and Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 4. Configure Environment Variables

The application uses a `.env` file to manage sensitive keys and configuration.

First, create a `.env` file in the project root. You can do this by copying the example file:

```bash
cp .env.example .env
```

Now, open the `.env` file and configure the following variables:

*   **`SECRET_KEY`**: This is crucial for session security. Change it to a long, random string.
*   **`MAIL_...` variables**: To send emails (for OTP verification and password resets), you must configure your SMTP server details. An example for Gmail is provided in the file. **Note:** If using Gmail, you may need to generate an "App Password" for your Google account.
*   **`DATABASE_URL`**: For production, you would set this to your PostgreSQL connection string. If left commented out, the application will default to using a local `site.db` SQLite database.

### 5. Install Dependencies

Install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 6. Set Up the Database

Run the database migrations to create the necessary tables.

```bash
# Set the Flask application entry point
export FLASK_APP=run.py

# Apply the database migrations
flask db upgrade
```

This will create a `site.db` file in the project root if you are using the default SQLite configuration.

---

## Running the Application

### 1. Create the First Admin User

Before you can log in as an administrator, you need to create the first admin account. Use the custom CLI command `create-admin` for this purpose.

Run the following command, replacing `<email>` and `<password>` with your desired credentials:

```bash
flask create-admin <email> <password>
```

**Example:**
```bash
flask create-admin admin@eduprep.com MySecurePassword123
```

This will create a new, verified user with the "Admin" role.

### 2. Run the Development Server

Once the setup is complete, you can start the Flask development server:

```bash
flask run
```

The application will be available at `http://127.0.0.1:5000`.

You can now navigate to the website in your browser and log in with the admin credentials you just created. From the admin dashboard, you can create additional users (Teachers, Students, etc.).

---

## Project Structure

*   `app/`: Main application package.
    *   `auth/`: Blueprint for authentication routes.
    *   `main/`: Blueprint for core application routes.
    *   `static/`: CSS, JavaScript, and image files.
    *   `templates/`: HTML templates.
        *   `admin/`, `auth/`, `email/`, `teacher/`: Subdirectories for organized templates.
    *   `commands.py`: Custom CLI commands.
    *   `email.py`: Email sending utility.
    *   `extensions.py`: Flask extension initializations.
    *   `models.py`: SQLAlchemy database models.
*   `migrations/`: Flask-Migrate database migration scripts.
*   `tests/`: Test files.
*   `run.py`: Application entry point.
*   `requirements.txt`: Python package dependencies.
*   `.env`: Environment variable configuration file.
*   `.gitignore`: Files and directories to be ignored by Git.