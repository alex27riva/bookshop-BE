import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from sample_data import book_data
from environment import Environment
from keycloak_url_gen import KeycloakURLGenerator
from keycloak_validator import KeycloakValidator
from models import db, Book, CartItem, User, WishlistItem
from functools import wraps

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Retrieve environment variables
env = Environment()

kc_url = KeycloakURLGenerator(base_url=env.KEYCLOAK_HOST, realm_name=env.REALM)

validator = KeycloakValidator(kc_url, env.CLIENT_ID)

app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///books.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'ThisIsNotASecureKeyForProduction!',
})
db.init_app(app)
CORS(app)  # Enable CORS for all routes


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the token from the request header
        auth_header = request.headers.get('Authorization')

        # Check if header exists and has the correct format
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        # Extract the token from the header
        token = auth_header.split("Bearer ")[-1]

        # Return user email
        result = validator.validate_token(token)

        if result:
            return func(result, *args, **kwargs)
        else:
            return jsonify({'error': 'Invalid token'}), 403  # Forbidden

    return wrapper


@app.route('/auth/check_token', methods=['POST'])
@jwt_required
def verify_token(email):
    return jsonify({'email': email}), 200


@app.route('/api/profile', methods=['GET'])
def profile():
    email = "email_from_token"
    return jsonify({"email": email})


@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    book_list = [{"id": book.id, "title": book.title, "author": book.author, "price": book.price, "cover_image_url": book.cover_image_url}
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
@app.route('/api/cart/add', methods=['POST'])
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
    # cart_item = CartItem(book_id=book_id, user_id=current_user.id)
    # db.session.add(cart_item)
    # db.session.commit()

    return jsonify({'message': 'Book added to cart successfully'}), 200


@app.route('/api/wishlist/add', methods=['POST'])
def add_to_wishlist():
    data = request.json
    user_id = data.get('user_id')
    book_id = data.get('book_id')

    # Check if both user_id and book_id are provided
    if user_id is None or book_id is None:
        return jsonify({'message': 'Both user_id and book_id are required.'}), 400

    # Check if user and book exist
    user = User.query.get(user_id)
    book = Book.query.get(book_id)

    if user is None:
        return jsonify({'message': f'User with id {user_id} not found.'}), 404

    if book is None:
        return jsonify({'message': f'Book with id {book_id} not found.'}), 404

    # Check if the book is already in the user's wishlist
    if WishlistItem.query.filter_by(user_id=user_id, book_id=book_id).first():
        return jsonify({'message': 'This book is already in the wishlist.'}), 400

    # Add the book to the user's wishlist
    wishlist_item = WishlistItem(user_id=user_id, book_id=book_id)
    db.session.add(wishlist_item)
    db.session.commit()

    return jsonify({'message': 'Book added to wishlist successfully.'}), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        for title, author, cover_image_url in book_data:
            # Check if book already exists
            if not Book.query.filter(Book.title == title).scalar():
                # Create and add book if not found
                book = Book(title=title, author=author, cover_image_url=cover_image_url)
                db.session.add(book)
        db.session.commit()

    app.run(debug=True)
