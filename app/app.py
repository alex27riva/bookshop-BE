import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from sample_data import book_data
from environment import Environment
from keycloak_url_gen import KeycloakURLGenerator
from keycloak_validator import KeycloakValidator
from models import db, Book, User, Wishlist
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
    'SECRET_KEY': env.SECRET_KEY if env.SECRET_KEY else 'ThisIsNotASecureKeyForProduction!',
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

        # Return TokenInfo object
        result = validator.validate_token(token)

        if result:
            return func(result, *args, **kwargs)
        else:
            return jsonify({'error': 'Invalid token'}), 403  # Forbidden

    return wrapper


@app.route('/api/signup', methods=['POST'])
@jwt_required
def create_account(token):
    """Creates a new user account from JWT info (name, surname, email) if unique.

    Returns:
        JSON: User creation message (success or already exists).
        Status code: 201 for created, 400 for existing user.
    """
    email = token.email
    if User.query.filter_by(email=email).first():
        logging.debug(f"Account for {email} already exists")
        return jsonify({"message": "User already registered"}), 200

    new_user = User(first_name=token.name, last_name=token.surname, email=email)
    db.session.add(new_user)
    db.session.commit()
    logging.debug(f"Account created for {email}")
    return jsonify({'message': 'User registered successfully.'}), 201


@app.route('/api/profile', methods=['GET'])
@jwt_required
def get_profile(token):
    """Retrieves the user profile associated with the JWT token.

    Returns:
        JSON: User data if found, error message otherwise.
        Status code: 200 for success, 404 for not found.
    """
    user = User.query.filter_by(email=token.email).first()
    if user:
        return jsonify(user.to_json()), 200
    return jsonify({"error": "User profile not found"}), 404


@app.route('/api/profile/picture', methods=['PUT'])
@jwt_required
def update_profile_picture(token):
    """Updates the user's profile picture URL based on the JWT token.

        Request Body:
            JSON: {'profile_pic_url': <new_url>} (new_url required)

        Returns:
            JSON: {'message': 'Profile picture URL updated successfully'} on success,
                   error message otherwise.
            Status code: 200 for success, 400 for bad request (missing URL), 404 for not found.
    """
    new_url = request.json.get('profile_pic_url')
    if not new_url:
        return jsonify({'error': 'Please provide a profile picture URL'}), 400

    user = User.query.filter_by(email=token.email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.profile_pic_url = new_url
    db.session.commit()
    logging.debug(f"Updated profile pic for {token.email} to {new_url}")
    return jsonify({'message': 'Profile picture URL updated successfully'}), 200


@app.route('/api/books', methods=['GET'])
def get_books():
    """Retrieves a list of all available books.

    Returns:
        JSON: A list of book data objects.
        Status code: 200 for success.
    """
    books = Book.query.all()
    book_list = [book.to_json() for book in books]
    return jsonify(book_list)


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Retrieves a book by its ID.

    URL Path Variable:
        <int:book_id>: The ID of the book to retrieve.

    Returns:
        JSON: Book data if found, error message otherwise.
        Status code: 200 for success, 404 for not found.
    """
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_json())
    else:
        return jsonify({"error": "Book not found"}), 404


@app.route('/api/admin/book', methods=['POST'])
@jwt_required
def add_new_book(token):
    """Adds a new book to the database if user has admin role

    Expects JSON data in the request body containing title, author,
    (optional) price, and (optional) cover_image_url.

    Returns:
        JSON:
            - message (str): 'Book added successfully' on success (201).
            - error (str): Reason for failure on errors (400, 409, 500)
    """
    if 'admin' not in token.roles:
        return jsonify({"error": "User is not admin"}), 403
    try:
        # Get JSON data from request body
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Missing data in request'}), 400

        # Extract book information
        b_title = data.get('title')
        b_author = data.get('author')
        b_price = data.get('price')
        b_cover_image_url = data.get('cover_image_url')

        if not all([b_title, b_author]):
            return jsonify({'error': 'Missing required fields (title, author)'}), 400

        # Check for duplicate book using unique combination (e.g., title + author)
        existing_book = db.session.query(Book).filter_by(title=b_title, author=b_author).first()

        if existing_book:
            logging.debug("Book already exists")
            return jsonify({'error': 'Book already exists in database'}), 409

        new_book = Book(title=b_title, author=b_author, price=b_price, cover_image_url=b_cover_image_url)

        db.session.add(new_book)
        db.session.commit()
        logging.debug("Book added from admin")
        return jsonify({'message': 'Book added successfully'}), 201

    except Exception as e:
        logging.error(e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/book/<int:book_id>', methods=['DELETE'])
@jwt_required
def delete_book_by_id(token, book_id):
    """Deletes a book from the database based on its ID, only if user is admin.

    Args:
        token (TokenInfo): JWT token
        book_id (int): The ID of the book to be deleted.

    Returns:
        JSON:
            - message (str): 'Book deleted successfully' on success (200).
            - error (str): Reason for failure on errors (404, 500).
    """
    if 'admin' not in token.roles:
        return jsonify({"error": "User is not admin"}), 403

    try:
        # Delete book with matching ID
        book_to_delete = Book.query.filter_by(id=book_id).first()

        if book_to_delete is None:
            return jsonify({'error': f'Book id:{book_id} not found'}), 404

        db.session.delete(book_to_delete)
        db.session.commit()

        return jsonify({'message': 'Book deleted successfully'}), 200

    except Exception as e:
        logging.debug(e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/wishlist', methods=['GET'])
@jwt_required
def get_wishlist(token):
    """Retrieves the user's wishlist associated with the JWT token.

    Returns:
        JSON: List of book data in user's wishlist if found,
               empty list if wishlist is empty,
               error message otherwise.
        Status code: 200 for success, 404 for user not found.
    """
    email = token.email
    db_user = User.query.filter_by(email=email).first()
    if db_user is None:
        return jsonify({'error': 'User not in the database'}), 404
    user_id = db_user.id

    # Get all wishlist items for the user
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()

    if not wishlist_items:
        logging.debug("Wishlist is empty")
        return jsonify({'wishlist': []}), 200  # Success with empty list

    # Build a list of book objects from wishlist items
    books = []
    for item in wishlist_items:
        book = Book.query.get(item.book_id)
        if book:
            books.append(book.to_json())  # Assuming a method to convert Book object to dict

    return jsonify({'wishlist': books}), 200


@app.route('/api/wishlist', methods=['POST'])
@jwt_required
def add_to_wishlist(token):
    """Adds a book to the user's wishlist based on the JWT token.

    Request Body:
        JSON: {'book_id': <book_id>} (book_id required)

    Returns:
        JSON: {'message': 'Book added to wishlist successfully.'} on success,
               error message otherwise.
        Status code: 201 for created, 400 for bad request (missing data, book not found, already in wishlist),
                     404 for user not found.
    """
    email = token.email
    data = request.json

    db_user = User.query.filter_by(email=email).first()
    if db_user is None:
        return jsonify({'error': 'User not in the database'}), 404
    user_id = db_user.id
    book_id = data.get('book_id')

    # Check if both user_id and book_id are provided
    if user_id is None or book_id is None:
        logging.debug(f"User_id and book_id are required, {user_id}, {book_id}")
        return jsonify({'error': 'Both user_id and book_id are required.'}), 400

    # Check if book exist
    book = Book.query.get(book_id)

    if book is None:
        return jsonify({'error': f'Book with id {book_id} not found.'}), 404

    # Check if the book is already in the user's wishlist
    if Wishlist.query.filter_by(user_id=user_id, book_id=book_id).first():
        return jsonify({'error': 'This book is already in the wishlist.'}), 200

    # Add the book to the user's wishlist
    wishlist_item = Wishlist(user_id=user_id, book_id=book_id)
    db.session.add(wishlist_item)
    db.session.commit()
    logging.debug(f"Book id {book_id} added wishlist")
    return jsonify({'message': 'Book added to wishlist successfully.'}), 201


@app.route('/api/wishlist/<int:book_id>', methods=['DELETE'])
@jwt_required
def remove_from_wishlist(token, book_id):
    """Removes a book from the user's wishlist based on the JWT token and book ID.

     URL Path Variable:
         <int:book_id>: The ID of the book to remove.

     Returns:
         JSON: {'message': 'Book removed from wishlist successfully.'} on success,
                error message otherwise.
         Status code: 200 for success, 400 for bad request (missing data, book not found, not in wishlist),
                      404 for user not found.
     """
    email = token.email

    db_user = User.query.filter_by(email=email).first()
    if db_user is None:
        return jsonify({'error': 'User not in the database'}), 404
    user_id = db_user.id

    # Check if both user_id and book_id are provided
    if user_id is None or book_id is None:
        return jsonify({'error': 'Both user_id and book_id are required.'}), 400

    # Check if book exist
    book = Book.query.get(book_id)

    if book is None:
        logging.debug(f"Book id {book_id} not found")
        return jsonify({'error': f'Book with id {book_id} not found.'}), 404

    # Check if the book is already in the user's wishlist
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, book_id=book_id).first()
    if wishlist_item is None:
        return jsonify({'error': 'This book is not in your wishlist.'}), 400

    # Remove the book from wishlist
    db.session.delete(wishlist_item)
    db.session.commit()
    logging.debug(f"Book id {book_id} removed from wishlist.")
    return jsonify({'message': 'Book removed from wishlist successfully.'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        for title, author, price, cover_image_url in book_data:
            # Check if book already exists
            if not Book.query.filter(Book.title == title).scalar():
                # Create and add book if not found
                book_to_add = Book(title=title, author=author, price=price, cover_image_url=cover_image_url)
                logging.debug(f"Added book {title}")
                db.session.add(book_to_add)
        db.session.commit()

    app.run(debug=True)
