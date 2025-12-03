from flask import Flask, render_template
from flask_restful import Api, request, Resource
from flask_bcrypt import Bcrypt
# Use the datetime module below to get the current datetime to insert for "last_login"
from datetime import datetime
from dotenv import load_dotenv
import pyodbc
import os

# The constants that you define should be placed at the top of the file, below imports.
MAX_USERNAME_LENGTH = 20
MIN_PASSWORD_LENGTH = 8


# Load environment variable if we're in development.
# Azure will always set the "WEBSITE_HOSTNAME" environment variable when running
# So we can use its presence to determine if we are on awa
# If we are not on awa, then we need to load the .secret.env file
if "WEBSITE_HOSTNAME" not in os.environ:
    # Development
    load_dotenv(".secret.env")


# We now load the connection string from the environment variable.
CONNECTION_STRING = os.environ["AZURE_SQL_CONNECTIONSTRING"]


# Initialize the flask app here
app = Flask(__name__)
# Initialize bcrypt for hashing passwords
flask_bcrypt = Bcrypt(app)
# Initialize the api
api = Api(app)


# This is a decorator function that we can use to easily add a reousrce at a specific route.
# Decorators are powerful!
def addResource(route: str):
    """Adds a resource to the API at the specified route"""

    def wrapper(cls, *args, **kwargs):
        api.add_resource(cls, route, *args, **kwargs)
        return cls

    return wrapper


# Database connection setup
# Normally, you would use something like SQLAlchemy to handle this and get pooling
# For now, we'll just stick to pyodbc
def get_db_connection():
    connection = pyodbc.connect(CONNECTION_STRING)
    return connection


# The "@app.route" decorator is sugar for calling app.add_url_rule
@app.route("/")
def index():
    return render_template("index.html", name="Flask Bootstrap5")



def validate_username(username: str, db_cursor: pyodbc.Cursor) -> tuple[bool, str]:
    """Validate the password to ensure it meets the requirements

    A username must be alphanumeric and at most 20 characters long.
    It must also not already exist in the database.

    @param username: The username to validate
    @param db_cursor: The cursor to the database
    @return: A tuple containing a boolean indicating if the username is valid and \
        an invalidation message if it is not (otherwise the empty string)
    """
    if not username.isalnum():
        return False, "Username must be alphanumeric"
    elif len(username) > MAX_USERNAME_LENGTH:
        return False, "Username must be at most 20 characters long"
    elif db_cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone():
        return False, "Username already exists"
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate the password to ensure it meets the requirements"

    @param password: The password to validate
    @return: A tuple containing a boolean indicating if the password is valid and \
        an invalidation message if it is not (otherwise the empty string)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    return True, ""


@app.route("/signin")
def signin():
    return render_template("signin.html")


# Now, we use the "addResource" decorator to add a resource at the "/register" route
# This is shorthand for calling "api.add_resource(Register, "/register")"
@addResource("/register")
class Register(Resource):
    def post(self):
        data = request.get_json()

        for key in ["username", "password", "displayName"]:
            if key not in data:
                return {"message": f"Missing required field: {key}"}, 400

        username = data.get("username")
        password = data.get("password")
        display_name = data.get("displayName")

        print("Recieving request: ", data)

        # Validate the password
        success, message = validate_password(password)
        if not success:
            return {"message": message}, 400

        # Validate the display name:

        if not display_name:
            return {"message": "Display name cannot be empty"}, 400

        # Save the user to the database

        # We use a context manager to ensure the connection is closed when we're done
        with get_db_connection() as conn:
            # A cursor grabs is an object that allows you to interact with the database.
            cursor = conn.cursor()

            # We made a function to validate the username to keep this code clean
            # check if the username already exists
            success, message = validate_username(username, cursor)
            if not success:
                return {"message": message}, 400

            # Hash the password. Do this after username checks to avoid unnecessary work
            hashed_password = flask_bcrypt.generate_password_hash(password).decode("utf-8")

            try:
                # This uses parameterized queries to avoid SQL injection
                # the ? is a placeholder that gets replaced by the values in the tuple
                cursor.execute(
                    "INSERT INTO Users (username, password, display_name) VALUES (?, ?, ?)",
                    (username, hashed_password, display_name),
                )
                cursor.commit()
            except pyodbc.Error:
                return {"message": "An error occurred while creating the user"}, 500
            finally:
                # We need to close the cursor to release the connection
                # Important to do this in a finally block to ensure it always happens regardless of the outcome
                cursor.close()

            return {"message": "User created successfully", "displayName": display_name}, 201


# Implement the login endpoint below.
# You will need to create a new resource class and add it to the API.
# The resource should be accessible at /login and should accept POST requests.
# The resource should accept a JSON object with a username and password field.
# It should check if the username exists in the database and if the password is correct

# You will need to write some SQL to get the password and display name from the database.
# Then, you will need to check, using bcrypt, that the passwords match.
# Look at the the python-api-activity part 2 to see how we did this before.

# then, edit the signin.js file to add logic for the login form.
# You will need to add the event handlers to the proper element IDs from the html.
# You can use the register form as a reference.

# @addResource("/login")
# class Login(Resource):
#     def post(self):
#  insert logic to get the username and password from the request.
#  Then, use the username to get the password, display name, and last login time from the database.
#  Check if the password is correct using bcrypt.
#  If the password is correct, return a success message
# Insert logic to call the database and check if the user exists
# If the user exists, check if the password is correct
# Finally, return a success message if the user exists that welcomes them back.
# Bonus points: Try to update the last login time in the database to the current time when the user logs in after a successful login.
# return {"message": f"Login successful, hello {displayName}, you last logged in at {lastLogin}"}, 200


if __name__ == "__main__":
    app.run(debug=True)
