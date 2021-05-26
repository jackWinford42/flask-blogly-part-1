"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

default_url = "https://bit.ly/3y8O4Be"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.Text, nullable=False, default=default_url)

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class PostTag(db.Model):
    __tablename__ = 'post_tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    tag = db.relationship(Tag, backref=db.backref("post_tags", cascade="all, delete-orphan"))
    post = db.relationship(Post, backref=db.backref("post_tags", cascade="all, delete-orphan"))

def connect_db(app):
    """Connect to database."""
    
    db.app = app
    db.init_app(app)