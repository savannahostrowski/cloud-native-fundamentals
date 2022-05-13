import logging
from multiprocessing import Value
import sqlite3
import sys

from flask import Flask, json, render_template, request, url_for, redirect, flash


logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

logging_stdout = logging.StreamHandler(sys.stdout).setLevel(logging.DEBUG)
logger.addHandler(logging_stdout)

logging_stderr = logging.StreamHandler(sys.stderr).setLevel(logging.WARNING)
logger.addHandler(logging_stderr)

connectionCounter = Value("i", 0)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connectionCounter.value += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.warning('404 - Article does not exist')
      return render_template('404.html'), 404
    else:
      app.logger.info('Article {} was retrieved.'.format(post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page was accessed.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    title=None
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
    
        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New article called {} was created'.format(title))
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/healthz')
def healthz():
    response = app.response_class(
        response = json.dumps({"result": "OK-healthy"}),
        status=200,
        mimetype="application/json"
    )
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = len(connection.execute('SELECT * FROM posts').fetchall())
    response = app.response_class(
        response = json.dumps({"db_connection_count": connectionCounter.value, "post_count": posts}),
        status=200
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
