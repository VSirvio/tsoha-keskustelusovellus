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
    current_msg = Message(db.session.execute(text(f"SELECT content FROM messages WHERE id = {msg_id}")).fetchone().content)
    replies = db.session.execute(text(f"SELECT descendant AS id FROM message_tree_paths WHERE ancestor = {msg_id} AND depth = 1")).fetchall()
    for reply in replies:
        current_msg.add_reply(select_msg_tree(reply.id))
    return current_msg

@app.route("/")
def message_list():
    first_msg = select_msg_tree(1)
    return render_template("messages.html", first_msg=first_msg)
