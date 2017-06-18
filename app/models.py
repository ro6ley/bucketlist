import os
import jwt
from flask_bcrypt import Bcrypt
from flask import current_app
from datetime import datetime, timedelta

from app.app import db
from instance.config import Config


class User(db.Model):
    """
    The model for a User
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    bucketlists = db.relationship('BucketList', order_by="BucketList.id",
                                  cascade="all,delete-orphan")

    def __init__(self, username, password, email):
        """
        Initialize the User with a username, email and password
        """
        self.username = username
        self.password = Bcrypt().generate_password_hash(password).decode()
        self.email = email

    def check_password(self, password):
        """
        Verify the password provided
        """
        return Bcrypt().check_password_hash(self.password, password)

    def generate_token(self, user_id):
        """
        Generates the access token
        """
        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # Create the byte string token using the payload and the Secret Key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get("SECRET"),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        """
        Decodes access token from Authorization Header
        """
        try:
            # try to decode the token from our secret variable
            payload = jwt.decode(token, current_app.config.get("SECRET"))
            return payload["sub"]

        except jwt.ExpiredSignatureError:
            # If the token has expired return an error
            return "Expired token. Please login to get a new one"

        except jwt.InvalidTokenError:
            # If the token is invalid, return and error
            return "Invalid token. Register or login"

    def save(self):
        """
        Save a user to the database
        """
        db.session.add(self)
        db.session.commit()


class BucketList(db.Model):
    """
    The model for the bucketlist
    """

    __tablename__ = "bucketlists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by

    def save(self):
        """
        Save a bucketlist
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        """
        Get all bucket lists
        """
        # return BucketList.query.all()
        return BucketList.query.filter_by(created_by=user_id)

    def get_items(self):
        """
        Returns all the items in a bucketlist
        """
        return Item.query.filter_by(bucketlist_id=BucketList.id)

    def delete(self):
        """
        Delete a bucketlist
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist: {}>".format(self.name)


class Item(db.Model):
    """
    The Model for an item
    """

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    done = db.Column(db.Boolean, default=False)
    # Foreign Key to Bucketlist
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(BucketList.id))

    def __init__(self, name, bucketlist_id):
        self.name = name
        self.bucketlist_id = bucketlist_id

    def save(self):
        """
        Save an item in a bucketlist
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_items(self):
        """
        Get all items in a bucketlists
        """
        return Item.query.filter_by(bucketlist_id=BucketList.id)

    def delete(self):
        """
        Delete an item in the bucketlist
        """
        db.session.delete(self)
        db.session.commit()
