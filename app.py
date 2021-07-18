"""Blogly application."""

from flask import Flask, request, redirect, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, PostTag, Tag

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret_key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

#USER

@app.route('/')
def home():
    """Homepage"""
    return redirect('/users')

@app.route('/users')    
def users_index():
    """List of users page"""

    users = User.query.all()
    return render_template('/users/index.html', users=users)

@app.route('/users/new_user', methods=['GET'])
def new_user_page():
    """Shows a form for new user (get request)"""
    return render_template('/users/new_user.html')

@app.route('/users/new_user', methods=['POST'])
def new_user_form():
    """Handle form submission for creating a new user (post request)"""

    new = User(first_name=request.form['first_name'], last_name=request.form['last_name'], image_url=request.form['image_url'] or None)

    db.session.add(new)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>')
def user_page(user_id):
    """Show information about given user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/user_page.html', user=user)

@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    """Show the edit page for a user (get request)"""

    user = User.query.get_or_404(user_id)
    return render_template('/users/edit.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def users_update(user_id):
    """Process the edit form to update an existing user (post request) """
    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def users_delete(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect('/users')

#POST

@app.route('/users/<int:user_id>/posts/new')
def show_new_form(user_id):
    """Show form to add a post for that user"""
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('posts/new_post.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_post(user_id):
    """Handle add form. add post and redirect to user detail page"""
    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist('tags')]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    new_post = Post(title=request.form['title'], 
                content=request.form['content'], user=user ,tags=tags)

    db.session.add(new_post)
    db.session.commit()
    
    return redirect(f"/users/{user_id}")

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show post"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('posts/post_detail.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    """Shows form to edit post"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('posts/edit.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def update_post(post_id):
    """Handle for submission for updating a post"""
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist('tags')]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Handle form submission to delete post"""
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")

#TAGS

@app.route('/tags')
def tags_list():
    """List of tags"""

    tags = Tag.query.all()
    return render_template('tags/list_tags.html', tags=tags)

@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """Show details about a tag"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show_tag.html', tag=tag)

@app.route('/tags/add-tag')
def add_tag_form():
    """Show form to create a new tag (get request)"""

    posts = Post.query.all()
    return render_template('tags/add_tag.html', posts=posts)

@app.route("/tags/add-tag", methods=['POST'])
def add_tag():
    """Handle form submission for creating a new tag (post request)"""
    post_ids = [int(num) for num in request.form.getlist('posts')]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts = posts)

    db.session.add(new_tag)
    db.session.commit()

    return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit')
def edit_tag_form(tag_id):
    """Show a form to edit tag (get request)"""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def edit_tag(tag_id):
    """Handle form submission for edit form (post request)"""
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist('posts')]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect('/tags')

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tags(tag_id):
    """Handle form submission for deleting a tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect('/tags')



