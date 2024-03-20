import logging
from flask import Flask, jsonify, request
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

from src.models import db, User, Role, Book, CartItem

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Retrieve environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
KEYCLOAK_TOKEN_ENDPOINT = os.getenv('KEYCLOAK_TOKEN_ENDPOINT')

app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///books.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'ThisIsNotASecureKeyForProduction!',
})
db.init_app(app)
CORS(app)  # Enable CORS for all routes
bcrypt = Bcrypt(app)



# Create the database
# db.create_all()

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# This route handles the callback from the Flutter frontend after authentication
@app.route('/auth/callback', methods=['POST'])
def handle_auth_callback():
    data = request.json
    logging.debug(f"Callback received {data}")
    authorization_code = data.get('code')

    if authorization_code:
        token_response = requests.post(KEYCLOAK_TOKEN_ENDPOINT, data={
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'code': authorization_code
        })
        logging.debug(f"Token response: {token_response}")

        if token_response.status_code == 200:
            access_token = token_response.json().get('access_token')
            logging.debug(f"Access token: {access_token}")
            # Now you have the access token, you can store it or use it as needed
            return jsonify({'access_token': access_token})
        else:
            logging.debug(f"Token response: {token_response.text}")

    return jsonify({'error': 'No authorization code provided'}), 400


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    password = data.get('password')

    # Check if the user already exists
    existing_user = user_datastore.find_user(email=email)
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = user_datastore.create_user(email=email, first_name=first_name, last_name=last_name,
                                          password=hashed_password, active=True)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = user_datastore.find_user(email=email)

    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@app.route('/api/profile', methods=['GET'])
@login_required
def profile():
    return jsonify({"email": current_user.email, "roles": [role.name for role in current_user.roles]})


@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    book_list = [{"id": book.id, "title": book.title, "author": book.author, "cover_image_url": book.cover_image_url}
                 for book in books]
    return jsonify(book_list)


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(
            {"id": book.id, "title": book.title, "author": book.author, "cover_image_url": book.cover_image_url})
    else:
        return jsonify({"error": "Book not found"}), 404


@app.route('/api/cart', methods=['GET'])
def get_cart_items():
    cart_items = CartItem.query.all()
    cart_list = [{"id": item.id, "book_id": item.book_id,
                  "book": {"id": item.book.id, "title": item.book.title, "author": item.book.author,
                           "cover_image_url": item.book.cover_image_url}} for item in cart_items]
    return jsonify(cart_list)


# Define your route for adding a book to the cart
@app.route('/api/add_to_cart', methods=['POST'])
@login_required  # Ensure user is authenticated via Keycloak OAuth
def add_to_cart():
    # Get data from request
    data = request.json
    book_id = data.get('book_id')

    # Check if book_id is provided
    if not book_id:
        return jsonify({'error': 'Book ID is required'}), 400

    # Check if the book exists
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # Create a new cart item for the current user
    cart_item = CartItem(book_id=book_id, user_id=current_user.id)
    db.session.add(cart_item)
    db.session.commit()

    return jsonify({'message': 'Book added to cart successfully'}), 200


# @app.route('/api/cart', methods=['POST'])
# @login_required
# def add_to_cart():
#     data = request.json
#     book_id = data.get('book_id')
#     book = Book.query.get(book_id)
#
#     if book:
#         cart_item = CartItem(book=book)
#         db.session.add(cart_item)
#         db.session.commit()
#         return jsonify({"message": "Book added to the cart"})
#     else:
#         return jsonify({"error": "Book not found"}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
