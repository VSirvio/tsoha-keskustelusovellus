import os
from flask import Flask, render_template, redirect, request, session, url_for
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv
from message_tree import Message

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL']
app.secret_key = os.environ['SECRET_KEY']
db = SQLAlchemy(app)

def select_msg_tree(msg_id : int):
    select_msg = text(
        f"SELECT content, username "
        f"FROM messages JOIN users "
        f"ON messages.id = {msg_id} AND users.id = messages.uid"
    )
    msg = db.session.execute(select_msg).fetchone()
    current_msg = Message(msg.username, msg_id, msg.content)

    select_replies = text(
        f"SELECT descendant AS id "
        f"FROM message_tree_paths "
        f"WHERE ancestor = {msg_id} AND depth = 1"
    )
    replies = db.session.execute(select_replies).fetchall()
    for reply in replies:
        current_msg.add_reply(select_msg_tree(reply.id))

    return current_msg

@app.route("/")
def signin():
    if "username" in session:
        return redirect(url_for('forums'))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    select_user = text(f"SELECT * FROM users WHERE username = :username")
    user = db.session.execute(select_user, {"username": username}).fetchone()

    if user and check_password_hash(user.password, password):
        session["username"] = username
        return redirect(url_for('forums'))

    return redirect(url_for('signin'))

@app.route("/logout")
def logout():
    del session["username"]
    return redirect(url_for("signin"))

@app.route("/forums")
def forums():
    if not "username" in session:
        return redirect(url_for('signin'))
    subforums = db.session.execute(text("SELECT * FROM subforums")).fetchall()
    return render_template("subforum_list.html", subforums=subforums)

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    if not "username" in session:
        return redirect(url_for('signin'))

    select_subforum = text(f"SELECT * FROM subforums WHERE id = {subforum_id}")
    cur_subforum = db.session.execute(select_subforum).fetchone()
    title = cur_subforum.title
    desc = cur_subforum.description

    select_thrs = text(f"SELECT * FROM threads WHERE subforum = {subforum_id}")
    thrs = db.session.execute(select_thrs).fetchall()

    return render_template("subforum.html", title=title, desc=desc, thrs=thrs)

@app.route("/thread/<int:thr_id>")
def thread(thr_id):
    if not "username" in session:
        return redirect(url_for('signin'))

    select_thr = text(f"SELECT * FROM threads WHERE id = {thr_id}")
    thread = db.session.execute(select_thr).fetchone()

    select_top_msg = text(
        f"SELECT id FROM messages WHERE thread = {thr_id} AND"
        f" (SELECT COUNT(*) FROM message_tree_paths WHERE descendant = id) = 1"
    )
    top_msg_id = db.session.execute(select_top_msg).fetchone().id
    top_msg = select_msg_tree(top_msg_id)

    return render_template("thread.html", thread=thread, top_msg=top_msg)

@app.route("/reply/<int:msg_id>")
def message(msg_id):
    if not "username" in session:
        return redirect(url_for('signin'))

    select_msg = text(f"SELECT thread FROM messages WHERE id = {msg_id}")
    thr_id = db.session.execute(select_msg).fetchone().thread

    return render_template("new_message.html", msg_id=msg_id, thr_id=thr_id)

@app.route("/send/<int:orig_id>", methods=["POST"])
def send(orig_id):
    if not "username" in session:
        return redirect(url_for('signin'))

    username = session["username"]
    select_user = text(f"SELECT id FROM users WHERE username = :username")
    user = db.session.execute(select_user, {"username": username}).fetchone()

    select_thr_id = text(f"SELECT thread FROM messages WHERE id = {orig_id}")
    thr_id = db.session.execute(select_thr_id).fetchone().thread

    content = request.form["content"]
    insert_msg = text(
        f"INSERT INTO messages "
        f"(uid, thread, content) VALUES ({user.id}, {thr_id}, :content) "
        f"RETURNING id"
    )
    msg = db.session.execute(insert_msg, {"content": content}).fetchone()
    db.session.commit()

    insert_self_path = text(
        f"INSERT INTO message_tree_paths "
        f"(ancestor, descendant, depth) VALUES ({msg.id}, {msg.id}, 0)"
    )
    db.session.execute(insert_self_path)
    insert_other_paths = text(
        f"INSERT INTO message_tree_paths "
        f"(ancestor, descendant, depth) "
        f"SELECT ancestor, {msg.id}, depth + 1"
        f" FROM message_tree_paths"
        f" WHERE descendant = {orig_id}"
    )
    db.session.execute(insert_other_paths)
    db.session.commit()

    return redirect(f"/thread/{thr_id}")

@app.route("/delete/<int:id>")
def delete(id):
    if not "username" in session:
        return redirect(url_for('signin'))

    select_message = text(f"SELECT uid, thread FROM messages WHERE id = {id}")
    msg = db.session.execute(select_message).fetchone()
    thr_id = msg.thread

    username = session["username"]
    select_user = text("SELECT id FROM users WHERE username = :user")
    cur_user = db.session.execute(select_user, {"user": username}).fetchone()
    if msg.uid != cur_user.id:
        return redirect(f"/thread/{thr_id}")

    select_paths = text(
        f"SELECT COUNT(*) AS paths "
        f"FROM message_tree_paths "
        f"WHERE descendant = {id}"
    )
    path_count = db.session.execute(select_paths).fetchone().paths

    delete_messages = text(
        f"DELETE FROM messages WHERE id "
        f"IN (SELECT descendant FROM message_tree_paths WHERE ancestor = {id})"
    )
    db.session.execute(delete_messages)
    delete_paths = text(
        f"DELETE FROM message_tree_paths WHERE descendant "
        f"IN (SELECT descendant FROM message_tree_paths WHERE ancestor = {id})"
    )
    db.session.execute(delete_paths)
    db.session.commit()

    if path_count == 1:
        select_subforum = text(f"SELECT * FROM threads WHERE id = {thr_id}")
        subforum_id = db.session.execute(select_subforum).fetchone().subforum

        db.session.execute(text(f"DELETE FROM threads WHERE id = {thr_id}"))
        db.session.commit()

        return redirect(f"/subforum/{subforum_id}")

    return redirect(f"/thread/{thr_id}")
