from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Represents a user in the system.

    Attributes:
        id (int): Unique identifier for the user (primary key).
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): User's email address (unique).
        password (str): Hashed password for the user. (not used)
        profile_pic_url (str, optional): URL of the user's profile picture.
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    profile_pic_url = db.Column(db.String)

    def to_json(self):
        """Converts the User object into a dictionary representation.

        Returns:
            dict: A dictionary containing user information
        """
        return {
            "id": self.id,
            "name": self.first_name,
            "surname": self.last_name,
            "email": self.email,
            "profile_pic_url": self.profile_pic_url
        }


# Define the Book model
class Book(db.Model):
    """Represents a book in the system.

    Attributes:
        id (int): Unique identifier for the book (primary key).
        title (str): Title of the book (not nullable).
        author (str): Author of the book (not nullable).
        price (float, optional): Price of the book.
        cover_image_url (str, optional): URL of the book's cover image.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Double)
    cover_image_url = db.Column(db.String(255))

    def to_json(self):
        """Converts the Book object into a dictionary representation.

        Returns:
            dict: A dictionary containing book information
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "price": self.price,
            "cover_image_url": self.cover_image_url
        }


# Define the CartItem model
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book = db.relationship('Book', backref=db.backref('cart_items', lazy=True))
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))


class Wishlist(db.Model):
    """Represents a book in a user's wishlist.

    Attributes:
        id (int): Unique identifier for the wishlist item (primary key).
        book_id (int): Foreign key referencing a book in the 'book' table (not nullable).
        user_id (int): Foreign key referencing a user in the 'user' table (not nullable).
        book (Book): Relationship with the Book model (one-to-many, lazy loading).
        user (User): Relationship with the User model (one-to-many, lazy loading).
    """
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book = db.relationship('Book', backref=db.backref('wishlist_items', lazy=True))
    user = db.relationship('User', backref=db.backref('wishlist_items', lazy=True))
