import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv
from message_tree import Message

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

def select_msg_tree(msg_id : int):
    select_msg = text(f"SELECT content FROM messages WHERE id = {msg_id}")
    msg_content = db.session.execute(select_msg).fetchone().content
    current_msg = Message(msg_content)

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
def index():
    subforums = db.session.execute(text("SELECT * FROM subforums")).fetchall()
    return render_template("subforum_list.html", subforums=subforums)

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    select_subforum = text(f"SELECT * FROM subforums WHERE id = {subforum_id}")
    cur_subforum = db.session.execute(select_subforum).fetchone()
    title = cur_subforum.title
    desc = cur_subforum.description

    select_thrs = text(f"SELECT * FROM threads WHERE subforum = {subforum_id}")
    thrs = db.session.execute(select_thrs).fetchall()

    return render_template("subforum.html", title=title, desc=desc, thrs=thrs)

@app.route("/thread/<int:thr_id>")
def thread(thr_id):
    select_thr = text(f"SELECT * FROM threads WHERE id = {thr_id}")
    thread = db.session.execute(select_thr).fetchone()

    select_top_msg = text(
        f"SELECT id FROM messages WHERE thread = {thr_id} AND"
        f" (SELECT COUNT(*) FROM message_tree_paths WHERE descendant = id) = 1"
    )
    top_msg_id = db.session.execute(select_top_msg).fetchone().id
    top_msg = select_msg_tree(top_msg_id)

    return render_template("thread.html", thread=thread, top_msg=top_msg)
