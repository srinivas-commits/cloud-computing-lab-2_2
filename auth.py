from flask import Flask, flash, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"

mydatabase = "data/socialmedia.db"

@app.route("/")
def index():
    if "user_id" in session:
        # User is logged in, show all posts
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        c.execute("SELECT * FROM posts")
        posts = c.fetchall()
        return render_template("all_posts.html", posts=posts)
    else:
        # User is not logged in, redirect to login page
        return redirect("/login")

@app.route("/my_posts")
def my_posts():
    if "user_id" in session:
        # User is logged in, show their own posts
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        user_id = session["user_id"]
        c.execute("SELECT * FROM posts WHERE user_id=?", (user_id,))
        posts = c.fetchall()
        return render_template("my_posts.html", posts=posts)
    else:
        # User is not logged in, redirect to login page
        return redirect("/login")

@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if "user_id" in session:
        # User is logged in, show the new post form
        if request.method == "POST":
            # Form submitted, create new post
            conn = sqlite3.connect(mydatabase)
            c = conn.cursor()
            title = request.form["title"]
            content = request.form["content"]
            user_id = session["user_id"]
            username = session["username"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO posts (user_id, title, content, username, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, title, content, username, timestamp))
            conn.commit()
            return redirect("/")
        else:
            # Show the new post form
            return render_template("new_post.html")
    else:
        # User is not logged in, redirect to login page
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Form submitted, check if username and password are correct
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        username = request.form["username"]
        password = request.form["password"]
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user is not None:
            # Username and password are correct, log the user in
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/")
        else:
            # Username and password are incorrect, show error message
            return render_template("login.html", error="Invalid username or password")
    else:
        # Show the login form
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Form submitted, create new user
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if user:
            return render_template("signup.html", error="Invalid username or password")
        
        # Create new user
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        return redirect("/login")
    else:
        # Show the signup form
        return render_template("signup.html")

@app.route("/userinfo", methods=["GET", "POST"])
def userinfo():
    if request.method == "GET":
        # Form submitted, create new user
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        user_id = session['user_id']
        c.execute("SELECT * FROM users WHERE id=?", (user_id, ))
        user = c.fetchone()
        return render_template("userinfo.html", user=user)
    else:
        # Show the signup form
        return render_template("all_posts.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    conn = sqlite3.connect(mydatabase)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL)')
    c.execute('CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, username TEXT NOT NULL, timestamp TEXT NOT NULL, user_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))')
    app.run(debug=True, host='0.0.0.0', port=5000)
