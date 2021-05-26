from unittest import TestCase
from app import app
from flask import session
from models import db, connect_db, User, Post, PostTag, Tag

class FlaskTests(TestCase):
    
    def setUp(self):
        """Initial variable declaration for set up"""

        self.client = app.test_client()
        
        app.config['TESTING'] = True
        User.query.delete()
        Tag.query.delete()
        PostTag.query.delete()
        Post.query.delete()
        db.session.commit()

    def test_user_list(self):
        """Ensure the users list has it's essential elements"""

        with self.client:
            response = self.client.get('/users')
            self.assertIn(b'<ul>', response.data)
            self.assertIn(b'<form action="/users/new">', response.data)
            self.assertIn(b'<input type="submit"', response.data)
    
    def test_add_user(self):
        """test adding a user on the add_user.html page"""

        with self.client:
            response = self.client.get('/users/new')
            self.assertIn(b'<form method="POST" action="/users/new">', response.data)
            self.assertIn(b'<label>Last Name</label>', response.data)
            self.assertIn(b'<input type="submit" value="Add user"></input>', response.data)
            self.client.post('/users/new')

    def test_edit_user(self):
        """test editing a user"""
        
        with self.client:
            user = User(
                first_name='test',
                last_name='user',
                image_url=None
            )
            db.session.add(user)
            db.session.commit()
            test_user_id = user.id
            response = self.client.get('/users/' + str(test_user_id) + '/edit')
            self.assertIn(b'<label>Last Name</label>', response.data)
            self.assertIn(b'<input type="submit" name="cancel_button" value="Cancel"></input>', response.data)
            self.assertIn(b'<input type="submit" name="save_button" value="Save"></input>', response.data)
            self.client.post('/users/' + str(test_user_id) + '/edit?first=test&last=edited&URL=&save_button=')
    
    def test_add_post(self):
        """test adding a post"""

        with self.client:
            response = self.client.get('users/1/posts/new')
            self.assertIn(b'<h2>Add Post for test user</h2>', response.data)
            self.assertIn(b'<label>Content</label>', response.data)
            self.assertIn(b'<textarea name="content" cols="40" rows="5"></textarea>', response.data)

    def test_add_tag(self):
        """test adding a tag"""

        with self.client:
            response = self.client.get('/tags/new')
            self.assertIn(b'<form method="POST" action="/tags/new">', response.data)
            self.assertIn(b'<label>Name</label>', response.data)
            self.assertIn(b'<input type="submit" name="add_button" value="Add"></input>', response.data)
            self.client.post('/tags/new?name=test')

    def test_list_tags(self):
        """test displaying the tag list page"""
        
        with self.client:
            response = self.client.get('/tags')
            self.assertIn(b'<ul>', response.data)
            self.assertIn(b'<li><a href="/tags/1">test</a></li>', response.data)
            self.assertIn(b'<input type="submit" value="add tag">', response.data)
            self.assertIn(b'<input type="submit" value="return to users">', response.data)

    def test_view_tag(self):
        """test displaying a single tag page and deleting that tag"""

        with self.client:
            response = self.client.get('/tags/1')
            self.assertIn(b'<ul>', response.data)
            self.assertIn(b'<form action="/tags/1">', response.data)
            self.assertIn(b'<input type="submit" name="delete_button" value="Delete"></input>', response.data)
            self.client.post('/tags/1?')

    def test_edit_post(self):
        """test editing a post"""

        with self.client:
            response = self.client.get('/posts/1/edit')
            self.assertIn(b'<h1>Edit Post</h1>', response.data)
            self.assertIn(b'<label>Content</label>', response.data)
            self.assertIn(b'<input type="submit" name="edit_button" value="Edit"></input>', response.data)
    
    def test_delete_post(self):
        """test deleting a post"""

        with self.client:
            self.client.get('/posts/1/delete')
            response = self.client.get('/users/1')


    def test_delete_user(self):
        """test deleting a user"""

        with self.client:
            self.client.get('users/1/delete')
            self.assertIsNone(session.get('test edited'))