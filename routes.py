import re
import secrets
from flask import render_template, redirect, abort, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from message_tree import Message
from app import app
import likes
import messages
import subforums
import threads
import users

def select_msg_tree(msg_id : int):
    msg = messages.get_msg(msg_id)
    user = users.get_user(session["username"])

    cur_msg = Message(msg.username, msg_id, msg.content)
    cur_msg.likes = likes.get_total_likes(msg_id)
    cur_msg.liked = likes.voted_by_user(msg_id, user.id)

    replies = messages.get_replies(msg_id)
    for reply in replies:
        cur_msg.add_reply(select_msg_tree(reply.id))

    return cur_msg

@app.route("/")
def signin():
    if "username" in session:
        return redirect(url_for("forums"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    if "username" in session:
        return redirect(url_for("forums"))

    username = request.form["username"]
    password = request.form["password"]

    if len(username) > 30:
        error_message = "Pisin sallittu tunnuksen pituus on 30 merkkiä"
        return render_template("login.html", error=error_message)

    if len(password) > 30:
        error_message = "Pisin sallittu salasanan pituus on 30 merkkiä"
        return render_template("login.html", error=error_message)

    user = users.get_user(username)

    if (not user) or (not check_password_hash(user.password, password)):
        error_message = "Virheellinen käyttäjätunnus tai salasana"
        return render_template("login.html", error=error_message)

    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)

    return redirect(url_for("forums"))

@app.route("/logout")
def logout():
    del session["username"]
    return redirect(url_for("signin"))

@app.route("/registration")
def registration():
    if "username" in session:
        return redirect(url_for("forums"))
    return render_template("registration.html")

@app.route("/register", methods=["POST"])
def register():
    if "username" in session:
        return redirect(url_for("forums"))

    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]

    error_message = None

    if len(username) < 5:
        error_message = "Lyhin sallittu tunnuksen pituus on 5 merkkiä"
    elif len(username) > 30:
        error_message = "Pisin sallittu tunnuksen pituus on 30 merkkiä"
    elif len(password) < 5:
        error_message = "Lyhin sallittu salasanan pituus on 5 merkkiä"
    elif len(password) > 30:
        error_message = "Pisin sallittu salasanan pituus on 30 merkkiä"
    elif password != password2:
        error_message = "Annetut salasanat eivät täsmää"
    elif users.get_user(username):
        error_message = "Antamasi tunnus on jo käytössä"

    if error_message:
        return render_template("registration.html", error=error_message)

    users.register(username, generate_password_hash(password))

    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)

    return redirect(url_for("forums"))

@app.route("/forums")
def forums():
    if "username" not in session:
        return redirect(url_for("signin"))
    forum_list = subforums.get_subforums()
    return render_template("subforum_list.html", subforums=forum_list,
                           is_admin=users.is_admin(session["username"]))

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    order_by = request.args.get("order_by")
    if order_by not in ["newest", "oldest", "most_liked", "most_disliked"]:
        order_by = "newest"

    cur_subforum = subforums.get_subforum(subforum_id)
    thrs = threads.get_thrs(subforum_id, order_by)

    return render_template("subforum.html", subforum=cur_subforum, thrs=thrs,
                           is_admin=users.is_admin(session["username"]),
                           order_by=order_by)

@app.route("/subforum/new")
def new_subforum():
    if "username" not in session:
        return redirect(url_for("signin"))

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    return render_template("new_subforum.html")

@app.route("/subforum/create", methods=["POST"])
def create_subforum():
    if "username" not in session:
        return redirect(url_for("signin"))

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    title = request.form["title"]
    desc = request.form["description"]

    if len(title) < 1 or len(title) > 30 or len(desc) < 1 or len(desc) > 100:
        return redirect(url_for("forums"))

    subforums.new_subforum(title, desc)

    return redirect(url_for("forums"))


@app.route("/subforum/delete/<int:subforum_id>")
def delete_subforum(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    subforums.delete_subforum(subforum_id)

    return redirect(url_for("forums"))

@app.route("/thread/<int:thr_id>")
def thread(thr_id):
    if "username" not in session:
        return redirect(url_for("signin"))
    thr = threads.get_thr(thr_id)
    first_msg = select_msg_tree(thr.first_msg)
    return render_template("thread.html", thread=thr, first_msg=first_msg,
                           is_admin=users.is_admin(session["username"]))

@app.route("/thread/new/<int:subforum_id>")
def new_thr(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))
    return render_template("new_thread.html", subforum_id=subforum_id)

@app.route("/thread/create/<int:subforum_id>", methods=["POST"])
def create_thr(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    title = request.form["title"]
    msg = request.form["message"]

    if len(title) < 1 or len(title) > 30 or len(msg) < 1 or len(msg) > 100:
        return redirect(url_for("new_thr", subforum_id=subforum_id))

    user = users.get_user(session["username"])
    thr_id = threads.new_thr(user.id, subforum_id, title, msg)

    return redirect(f"/thread/{thr_id}")

@app.route("/thread/edit/<int:thr_id>")
def edit_thr(thr_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    is_admin = users.is_admin(session["username"])
    thr = threads.get_thr(thr_id)

    if session["username"] != thr.username and not is_admin:
        return redirect(url_for("thread", thr_id=thr_id))

    return render_template("edit_thread.html", thr=thr)

@app.route("/thread/save/<int:thr_id>", methods=["POST"])
def save_thr(thr_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    is_admin = users.is_admin(session["username"])
    thr = threads.get_thr(thr_id)

    if session["username"] != thr.username and not is_admin:
        return redirect(url_for("thread", thr_id=thr_id))

    title = request.form["title"]

    if len(title) < 1 or len(title) > 30:
        return redirect(url_for("edit_thr", thr_id=thr_id))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    threads.edit_thr(thr_id, title)

    return redirect(url_for("thread", thr_id=thr_id))

@app.route("/thread/delete/<int:thr_id>")
def delete_thr(thr_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    is_admin = users.is_admin(session["username"])
    thr = threads.get_thr(thr_id)

    if session["username"] != thr.username and not is_admin:
        return redirect(url_for("subforum", subforum_id=thr.subforum))

    threads.delete_thr(thr_id)

    return redirect(url_for("subforum", subforum_id=thr.subforum))

@app.route("/reply/<int:msg_id>")
def message(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))
    thr_id = messages.get_msg(msg_id).thread
    return render_template("new_message.html", msg_id=msg_id, thr_id=thr_id)

@app.route("/send/<int:orig_id>", methods=["POST"])
def send(orig_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    content = request.form["content"]

    if len(content) < 1 or len(content) > 1000:
        return redirect(url_for("message"))

    user = users.get_user(session["username"])
    thr_id = messages.get_msg(orig_id).thread
    messages.new_msg(orig_id, user.id, thr_id, content)

    return redirect(f"/thread/{thr_id}")

@app.route("/edit/<int:msg_id>")
def edit(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    user = users.get_user(session["username"])
    msg = messages.get_msg(msg_id)

    if user.id != msg.uid and not user.admin:
        return redirect(url_for("thread", thr_id=msg.thread))

    return render_template("edit_message.html", msg=msg)

@app.route("/save/<int:msg_id>", methods=["POST"])
def save(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    user = users.get_user(session["username"])
    msg = messages.get_msg(msg_id)

    if user.id != msg.uid and not user.admin:
        return redirect(url_for("thread", thr_id=msg.thread))

    content = request.form["content"]

    if len(content) < 1 or len(content) > 100:
        return redirect(url_for("edit", msg_id=msg_id))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    messages.edit_msg(msg_id, content)

    return redirect(url_for("thread", thr_id=msg.thread))

@app.route("/delete/<int:msg_id>")
def delete(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    msg = messages.get_msg(msg_id)

    cur_user = users.get_user(session["username"])
    if msg.uid != cur_user.id and not users.is_admin(session["username"]):
        return redirect(f"/thread/{msg.thread}")

    is_1st_msg = messages.is_1st_msg_in_thr(msg_id)
    subforum_id = threads.get_subforum_id(msg.thread)

    messages.delete_msg(msg_id)

    if is_1st_msg:
        return redirect(f"/subforum/{subforum_id}")

    return redirect(f"/thread/{msg.thread}")

@app.route("/like/<int:msg_id>")
def like(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    user = users.get_user(session["username"])

    likes.like(user.id, msg_id)

    return redirect(f"/thread/{messages.get_msg(msg_id).thread}")

@app.route("/dislike/<int:msg_id>")
def dislike(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    user = users.get_user(session["username"])

    likes.dislike(user.id, msg_id)

    return redirect(f"/thread/{messages.get_msg(msg_id).thread}")

@app.route("/unlike/<int:msg_id>")
def unlike(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    user = users.get_user(session["username"])

    likes.unlike(user.id, msg_id)

    return redirect(f"/thread/{messages.get_msg(msg_id).thread}")

@app.route("/search", methods=["POST"])
def search():
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    search_terms = re.findall(r"\w+", request.form["search_terms"].lower())

    if len(search_terms) < 1 or len(search_terms) > 10:
        return redirect(url_for("forums"))

    results = messages.search(search_terms)

    return render_template("search_results.html", results=results)
