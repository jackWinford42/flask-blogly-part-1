"""Blogly application."""

from flask import Flask, render_template, redirect, request
from models import db, connect_db, User, Post, PostTag, Tag

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

@app.route('/users/<user_id>/posts/new', methods = ['POST', 'GET'])
def new_post(user_id):
    """display a form for adding a new post and on Post handle the form"""

    user = User.query.get_or_404(user_id)

    if request.method == 'GET':

        return_url = "/users/" + user_id + "/posts/new"
        tags = Tag.query.order_by(Tag.name).all()
        return render_template('add_post.html',
                                user=user,
                                return_url=return_url,
                                tags=tags)
    else:
        try:
            request.form['save_button']

            post = Post(
                title=request.form['title'],
                content=request.form['content'],
                user_id=user_id
            )
            db.session.add(post)

            tag_array_of_tuples = db.session.query(Tag.id).all()

            for tag_tuple in tag_array_of_tuples:

                number = str(tag_tuple[0])

                try:
                    #if a tag is checked then there is no error
                    # and it is added to the PostTag database
                    request.form[number]
                    tagged = PostTag(
                        post_id=post.id,
                        tag_id=number
                    )
                    db.session.add(tagged)
                except Exception:
                    pass

            db.session.commit()

            return redirect('/users')
        except Exception:

            return redirect('/users')

@app.route('/posts/<post_id>', methods = ['POST', 'GET'])
def post(post_id):
    """display a post along with options to interact with the post"""
    post = Post.query.get_or_404(post_id)
    return_url = '/posts/' + post_id
    if request.method == 'GET':
        #get an array of tuples for all the tags on this post
        tag_array_of_tuples = db.session.query(PostTag.tag_id).filter_by(post_id=post_id).all()
        
        tags = []

        for tag_tuple in tag_array_of_tuples:
            tag_id = str(tag_tuple[0])
            tags.append(Tag.query.get_or_404(tag_id))

        return render_template('post.html',
                                post=post,
                                return_url=return_url,
                                tags=tags)
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
    post = Post.query.get_or_404(post_id)

    if request.method == 'GET':
        #get the post and tag relationships for the given post
        tag_array_of_tuples = db.session.query(PostTag.tag_id).filter_by(post_id=post_id).all()

        checked_tags = []

        #convert the list of tuples into a list of tags associated with the given post 
        for tag_tuple in tag_array_of_tuples:
            tag_id = str(tag_tuple[0])
            checked_tags.append(Tag.query.get_or_404(tag_id))
        
        tags = Tag.query.order_by(Tag.id).all()

        #loop through the list of existing tags and delete the ones that are already
        #associated with the given post
        i = 0
        while i < len(tags):
            tag = tags[i]
            if tag in checked_tags:
                del tags[i]
            else:
                i = i + 1

        return_url = "/posts/" + post_id + "/edit"
        return render_template('edit_post.html',
                                post=post,
                                return_url=return_url,
                                tags=tags,
                                checked_tags=checked_tags)
    else:
        view_post = '/posts/' + post_id
        try:
            request.form['edit_button']

            post.title = request.form['title']
            post.content = request.form['content']
            db.session.add(post)

            tag_array_of_tuples = db.session.query(Tag.id).all()
            #loop through every existing tag
            for tag_tuple in tag_array_of_tuples:

                number = str(tag_tuple[0])
                try:
                    request.form[number]

                    #if the relationship between this tag and this post does not exist already
                    if not PostTag.query.filter_by(post_id=post_id, tag_id=number).one_or_none():

                        tagged = PostTag(
                            post_id=post_id,
                            tag_id=number
                        )
                        #add the tag relationship to the PostTag database
                        db.session.add(tagged)
                except Exception:
                    #exception is triggered if a tag is not checked
                    try:
                        #if tag and post relationship already exists in the PostTag database
                        if PostTag.query.filter_by(post_id=post_id, tag_id=number).one_or_none():

                            relationship = PostTag.query.filter_by(post_id=post_id, tag_id=number).one_or_none()
                            #delete the relationship
                            db.session.delete(relationship)
                    except Exception:
                        pass
            db.session.commit()

            return redirect(view_post)
        except Exception:
            return redirect(view_post)

@app.route('/posts/<post_id>/delete', methods = ['GET', 'POST'])
def delete_post(post_id):
    """delete a post then redirect to the users list"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/users')

@app.route('/tags')
def display_tags():
    """display a list of all the tags in the tags table"""

    tags = Tag.query.order_by(Tag.name).all()

    return render_template('tag_list.html',
                            title='Tags',
                            tags=tags)

@app.route('/tags/<tag_id>')
def display_single_tag(tag_id):
    """display a single tag and it's associated posts"""

    tag = Tag.query.get_or_404(tag_id)

    postTagsNotTheTable = PostTag.query.filter_by(tag_id=tag_id).all()

    return render_template('tag.html',
                            title=tag.name,
                            tag=tag,
                            )

@app.route('/tags/new', methods = ['GET', 'POST'])
def add_tag():
    """display the page to add a new tag"""

    if request.method == 'GET':
        return render_template('add_tag.html',
                                title='Create a tag')
    else:
        try:
            request.form['add_button']
            tag = Tag(
                name=request.form['name']
            )
            db.session.add(tag)
            db.session.commit()
            return redirect('/tags')
        except Exception:
            return redirect('/tags')