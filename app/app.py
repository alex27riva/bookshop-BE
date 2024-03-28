import logging

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, login_required, current_user

from environment import Environment
from keycloak_url_gen import KeycloakURLGenerator
from keycloak_validator import KeycloakValidator
from models import db, User, Role, Book, CartItem

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Retrieve environment variables
env = Environment()

kc_url = KeycloakURLGenerator(base_url=env.KEYCLOAK_HOST, realm_name=env.REALM)

validator = KeycloakValidator(kc_url.certs_url(), env.CLIENT_ID)

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


@app.route('/auth/check_token', methods=['POST'])
def verify_token():
    # Get the token from the request header
    auth_header = request.headers.get('Authorization')

    # Check if header exists and has the correct format
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401

    # Extract the token from the header
    token = auth_header.split("Bearer ")[-1]

    logging.debug(token)
    if validator.validate_token(token):
        # Token is valid, proceed with your application logic
        return jsonify({'message': 'Token is valid'}), 200
    else:
        # Token is invalid or expired, handle accordingly
        return jsonify({'error': 'Token is invalid'}), 200


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

        book_data = [
            ('1984', 'George Orwell', 'https://www.bookerworm.com/images/1984.jpg'),
            ('Brave New World', 'Aldous Huxley',
             'https://upload.wikimedia.org/wikipedia/en/6/62/BraveNewWorld_FirstEdition.jpg'),
        ]

        for title, author, cover_image_url in book_data:
            # Check if book already exists
            if not Book.query.filter(Book.title == title).scalar():
                # Create and add book if not found
                book = Book(title=title, author=author, cover_image_url=cover_image_url)
                db.session.add(book)
        db.session.commit()

    app.run(debug=True)
