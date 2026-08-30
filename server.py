#!/usr/bin/env python3

from flask import (
    Flask,
    request,
    session,
    redirect,
    url_for,
    jsonify,
    send_from_directory
)

from functools import wraps
from datetime import datetime
import os
import secrets
import json


# ============================================================
# SETUP
# ============================================================

app = Flask(__name__)

ADMIN_PASSWORD = "dorm123"

app.secret_key = secrets.token_hex(32)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ADMIN_DIR = os.path.join(
    BASE_DIR,
    "admin"
)

ADDPOST_DIR = os.path.join(
    BASE_DIR,
    "addpost"
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "posts.json"
)


# ============================================================
# FILE STORAGE
# ============================================================

def load_posts():

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return []


def save_posts(posts):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            posts,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# MAIN PAGE
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        BASE_DIR,
        "index.html"
    )


@app.route("/style.css")
def style():

    return send_from_directory(
        BASE_DIR,
        "style.css"
    )


@app.route("/script.js")
def script():

    return send_from_directory(
        BASE_DIR,
        "script.js"
    )


# ============================================================
# ADD POST PAGE
# ============================================================

@app.route("/addpost/")
def addpost():

    return send_from_directory(
        ADDPOST_DIR,
        "index.html"
    )


# ============================================================
# PUBLIC POST API
# ============================================================

@app.route(
    "/api/posts",
    methods=["GET"]
)
def get_posts():

    posts = load_posts()

    # Newest posts first
    posts.sort(
        key=lambda post:
        post.get("created", ""),
        reverse=True
    )

    return jsonify(posts)


# ============================================================
# CREATE POST
# ============================================================

@app.route(
    "/api/posts",
    methods=["POST"]
)
def create_post():

    data = request.get_json()

    if not data:

        return jsonify({
            "error":
            "No data received."
        }), 400


    alias = data.get(
        "alias",
        ""
    ).strip()


    message = data.get(
        "message",
        ""
    ).strip()


    # Validate alias

    if not alias:

        return jsonify({
            "error":
            "Alias is required."
        }), 400


    if len(alias) > 30:

        return jsonify({
            "error":
            "Alias is too long."
        }), 400


    # Validate message

    if not message:

        return jsonify({
            "error":
            "Message is required."
        }), 400


    if len(message) > 500:

        return jsonify({
            "error":
            "Message is too long."
        }), 400


    # Create post

    posts = load_posts()


    post = {

        "id":
        secrets.token_hex(8),

        "alias":
        alias,

        "message":
        message,

        "created":
        datetime.now().isoformat(
            timespec="seconds"
        )

    }


    posts.append(post)

    save_posts(posts)


    return jsonify({
        "success": True,
        "post": post
    }), 201


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/",
    methods=["GET", "POST"]
)
def admin_login():

    # Already logged in
    if session.get("admin"):

        return redirect(
            url_for("admin_panel")
        )


    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )


        if secrets.compare_digest(
            password,
            ADMIN_PASSWORD
        ):

            session["admin"] = True

            return redirect(
                url_for("admin_panel")
            )


        return """
        <!DOCTYPE html>

        <html>

        <head>
            <title>Login Failed</title>
        </head>

        <body>

            <h2>Incorrect password</h2>

            <a href="/admin/">
                Try again
            </a>

        </body>

        </html>
        """


    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>Free Wall Admin</title>

        <link
            rel="stylesheet"
            href="/style.css"
        >

    </head>


    <body>

        <header>

            <h1>Free Wall</h1>

            <p>Administrator Login</p>

        </header>


        <main>

            <section class="card">

                <h2>Admin Login</h2>


                <form method="POST">

                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        required
                    >


                    <button type="submit">
                        Login
                    </button>

                </form>


                <br>


                <a href="/">
                    ← Back to Free Wall
                </a>

            </section>

        </main>

    </body>

    </html>
    """


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("admin"):

            return jsonify({
                "error":
                "Authentication required."
            }), 401

        return function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# ADMIN PANEL
# ============================================================

@app.route("/admin/panel")
def admin_panel():

    if not session.get("admin"):

        return redirect(
            url_for("admin_login")
        )


    return send_from_directory(
        ADMIN_DIR,
        "index.html"
    )


# ============================================================
# ADMIN DELETE POST
# ============================================================

@app.route(
    "/api/posts/<post_id>",
    methods=["DELETE"]
)
@admin_required
def delete_post(post_id):

    posts = load_posts()


    new_posts = [

        post

        for post in posts

        if post.get("id") != post_id

    ]


    if len(new_posts) == len(posts):

        return jsonify({
            "error":
            "Post not found."
        }), 404


    save_posts(new_posts)


    return jsonify({
        "success": True
    })


# ============================================================
# LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect("/")


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("==============================")
    print("       FREE WALL ONLINE")
    print("==============================")
    print()
    print("Main:")
    print("http://127.0.0.1:8080/")
    print()
    print("Add Post:")
    print("http://127.0.0.1:8080/addpost/")
    print()
    print("Admin:")
    print("http://127.0.0.1:8080/admin/")
    print()


    app.run(
        host="0.0.0.0",
        port=8080
    )
