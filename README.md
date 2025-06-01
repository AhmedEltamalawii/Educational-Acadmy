# To Run Web Application --> run.py
from pythonic import app
if __name__ == "__main__":
    app.run(debug=True)
# Flask Web Application

This project is a web application built using the Flask framework. It includes features for user management, course and lesson handling, and administrative functionalities, with database integration and support for running via Docker.

## Features

*   **User Authentication:** Secure user login and management using Flask-Login.
*   **Course Management:** Functionality to handle courses.
*   **Lesson Management:** Functionality to handle lessons within courses.
*   **Admin Panel:** Administrative routes for managing the application.
*   **Database Integration:** Uses Flask-SQLAlchemy for database interactions.
*   **Forms:** Handles web forms using Flask-WTF.
*   **Email Support:** Includes Flask-Mail for sending emails.
*   **Image Handling:** Uses Pillow, likely for processing user avatars or other images.
*   **Database Management Scripts:** Includes scripts for initializing, resetting, checking, and adding test data to the database.
*   **User Creation Script:** Script to create an admin user.
*   **Docker Support:** Includes `Dockerfile` and `docker-compose.yml` for containerized deployment.

## Technologies Used

*   Flask
*   Flask-SQLAlchemy
*   Flask-Login
*   Flask-WTF
*   Flask-Mail
*   Werkzeug
*   Pillow
*   email-validator

## Project Structure

*   `flasktest/`: Contains the main application code and configuration.
    *   `__pycache__/`: Python cache files.
    *   `migrations/`: Database migration scripts.
    *   `pythonic/`: Contains the core application modules (routes, models, forms, utils).
        *   `admin_routes.py`: Routes for administrative tasks.
        *   `course_routes.py`: Routes for course-related functionalities.
        *   `forms.py`: Definition of web forms.
        *   `routes.py`: General application routes.
        *   `models.py`: Database models using SQLAlchemy.
        *   `lesson_routes.py`: Routes for lesson-related functionalities.
        *   `utils.py`: Utility functions.
    *   `.dockerignore`: Specifies files to ignore when building the Docker image.
    *   `check_db.py`: Script to check the database status.
    *   `add_test_data.py`: Script to add test data to the database.
    *   `create_admin.py`: Script to create an admin user.
    *   `docker-compose.yml`: Docker Compose file for defining and running multi-container Docker applications.
    *   `Dockerfile`: Defines the Docker image for the application.
    *   `run.py`: Entry point to run the Flask application.
    *   `reset_db.py`: Script to reset the database.
    *   `requirements.txt`: Lists the project dependencies.
    *   `init_db.py`: Script to initialize the database.

## Setup and Installation

### Using Docker (Recommended)

1.  Make sure you have Docker and Docker Compose installed.
2.  Navigate to the `flasktest` directory in your terminal.
3.  Build and run the containers:
    ```bash
    docker-compose up --build
    ```
4.  The application should be accessible at `http://localhost:5000` (or the port specified in `docker-compose.yml`).

### Manual Setup

1.  Make sure you have Python 3 installed.
2.  Navigate to the `flasktest` directory in your terminal.
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up the database (you might need to configure your database connection string first, likely in a configuration file not shown in the structure):
    ```bash
    python init_db.py
    # You might also want to run migrations if any
    # python create_admin.py # To create an admin user
    # python add_test_data.py # To add test data
    ```
5.  Run the application:
    ```bash
    python run.py
    ```
6.  The application should be accessible at `http://127.0.0.1:5000`.

## Database Management

The project includes several scripts for database management:

*   `init_db.py`: Initializes the database.
*   `reset_db.py`: Resets the database.
*   `check_db.py`: Checks the database status.
*   `add_test_data.py`: Adds test data to the database.
*   `create_admin.py`: Creates an initial admin user.

