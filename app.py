"""Blogly application."""

from flask import Flask, render_template, redirect, request
from models import db, connect_db, User

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
    edit_url = '/users/' + user_id + '/edit'
    delete_url = '/users/' + user_id + '/delete'

    return render_template('user.html',
                            user=user,
                            edit_url=edit_url,
                            delete_url=delete_url)

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

            db.session.delete(user)
            user = User(
                first_name=request.form['first'],
                last_name=request.form['last'],
                image_url=request.form['URL'] or None
            )
            db.session.add(user)
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