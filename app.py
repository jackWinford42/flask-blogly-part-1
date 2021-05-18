"""Blogly application."""

from flask import Flask, render_template, redirect, request
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

from flask_debugtoolbar import DebugToolbarExtension
app.config['SECRET_KEY'] = "thisIsSecret"
debug = DebugToolbarExtension(app)

@app.route('/')
def redirect_to_users():
    """root route redirects to users route"""

    return redirect('/users')

@app.route('/users')
def list_users():
    """Display a list of all the users in the database"""

    users = User.query.order_by(User.last_name, User.first_name).all()

    return render_template('list.html',
                            title='Users',
                            users=users)

@app.route('/users/new', methods = ['POST', 'GET'])
def new_user():
    """display a form where a new user can be added"""

    if request.method == 'GET':
        return render_template('add_user.html')
    else:
        user = User(
            first_name=request.form['first'],
            last_name=request.form['last'],
            image_url=request.form['URL'] or None
        )

        db.session.add(user)
        db.session.commit()
        
        return redirect('/users')

@app.route('/users/<user_id>')
def user_page(user_id):
    """display the page for a single user"""

    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).all()
    edit_url = '/users/' + user_id + '/edit'
    delete_url = '/users/' + user_id + '/delete'

    return render_template('user.html',
                            user=user,
                            edit_url=edit_url,
                            delete_url=delete_url,
                            posts=posts)

@app.route('/users/<user_id>/edit', methods = ['POST', 'GET'])
def edit_user(user_id):
    """display a page where the details of a single user can be changed"""

    user = User.query.get_or_404(user_id)

    if request.method == 'GET':
        
        return_url = "/users/" + user_id + "/edit"
        return render_template('edit.html',
                                user=user,
                                return_url=return_url)
    else:

        try:
            request.form['save_button']

            user.first_name = request.form['first']
            user.last_name = request.form['last']
            user.image_url = request.form['URL'] or None

            db.session.commit()
            return redirect('/users')
        except Exception:
            return redirect('/users')

@app.route('/users/<user_id>/delete')
def delete_user(user_id):
    """delete a user based off their ID then display the users page"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<user_id>/posts/new', methods = ['POST', 'GET'])
def new_post(user_id):
    """display a form for adding a new post and on Post handle the form"""

    user = User.query.get_or_404(user_id)

    if request.method == 'GET':

        return_url = "/users/" + user_id + "/posts/new"
        return render_template('add_post.html',
                                user=user,
                                return_url=return_url)
    else:
        try:
            request.form['save_button']

            post = Post(
                title=request.form['title'],
                content=request.form['content'],
                user_id=user_id
            )
            db.session.add(post)
            db.session.commit()
            return redirect('/users')
        except Exception:
            return redirect('/users')

@app.route('/posts/<post_id>', methods = ['POST', 'GET'])
def post(post_id):
    """display a post along with options to interact with the post"""
    post = Post.query.filter_by(id=post_id).first()
    return_url = '/posts/' + post_id
    if request.method == 'GET':
        return render_template('post.html',
                                post=post,
                                return_url=return_url)
    else:
        try:
            request.form['cancel_button']

            return redirect('/users')
        except Exception:
            try:
                request.form['edit_button']
                edit_url = '/posts/' + post_id + '/edit'
                return redirect(edit_url) 
            except Exception:
                try:
                    request.form['delete_button']
                    delete_url = '/posts/' + post_id + '/delete'

                    return redirect(delete_url)
                except Exception:
                    return redirect(return_url)

@app.route('/posts/<post_id>/edit', methods = ['POST', 'GET'])
def edit_post(post_id):
    """display the page to edit a post then process the edit or cancel"""
    post = Post.query.filter_by(id=post_id).first()

    if request.method == 'GET':

        return_url = "/posts/" + post_id + "/edit"
        return render_template('edit_post.html',
                                post=post,
                                return_url=return_url)
    else:
        view_post = '/posts/' + post_id
        try:
            request.form['edit_button']

            post.title = request.form['title']
            post.content = request.form['content']

            db.session.commit()

            return redirect(view_post)
        except Exception:
            return redirect(view_post)

@app.route('/posts/<post_id>/delete', methods = ['GET', 'POST'])
def delete_post(post_id):
    """delete a post then redirect to the users list"""
    post = Post.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('/users')