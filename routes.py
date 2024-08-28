import re
import secrets
import unicodedata
from flask import flash, render_template, redirect, abort, request, session, \
                  url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
import config
import likes
import messages
import permissions
import subforums
import threads
import users

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

    error = False

    if len(username) > 30:
        flash("Pisin sallittu tunnuksen pituus on 30 merkkiä")
        error = True

    if len(password) > 30:
        flash("Pisin sallittu salasanan pituus on 30 merkkiä")
        error = True

    if error:
        return redirect(url_for("signin"))

    user = users.get_user(username)

    if (not user) or (not check_password_hash(user.password, password)):
        flash("Virheellinen käyttäjätunnus tai salasana")
        return redirect(url_for("signin"))

    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)

    return redirect(url_for("forums"))

@app.route("/logout", methods=["POST"])
def logout():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    del session["username"]

    return redirect(url_for("signin"))

@app.route("/registration")
def registration():
    if "username" in session:
        return redirect(url_for("forums"))
    return render_template("registration.html",
                           allowed_chars=config.USERNAME_ALLOWED_CHARS,
                           invalid_username_msg=config.INVALID_USERNAME_MSG)

@app.route("/register", methods=["POST"])
def register():
    if "username" in session:
        return redirect(url_for("forums"))

    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]

    error = False

    if len(username) < 5 or len(username) > 30:
        flash("Tunnuksen tulee olla 5-30 merkin pituinen")
        error = True

    if re.search(f"[^{config.USERNAME_ALLOWED_CHARS}]", username):
        flash(config.INVALID_USERNAME_MSG)
        error = True

    if len(password) < 5 or len(password) > 30:
        flash("Salasanan tulee olla 5-30 merkin pituinen")
        error = True

    if password != password2:
        flash("Annetut salasanat eivät täsmää")
        error = True

    if users.get_user(username):
        flash("Antamasi tunnus on jo käytössä")
        error = True

    if error:
        return redirect(url_for("registration"))

    users.register(username, generate_password_hash(password))

    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)

    return redirect(url_for("forums"))

@app.route("/forums")
def forums():
    if "username" not in session:
        return redirect(url_for("signin"))

    forum_list = subforums.get_subforums(session["username"])

    return render_template("subforum_list.html", subforums=forum_list,
                           is_admin=users.is_admin(session["username"]))

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if not subforums.is_permitted(subforum_id, session["username"]):
        return redirect(url_for("forums"))

    order_by = request.args.get("order_by")
    if order_by not in ["newest", "oldest", "most_liked", "most_disliked"]:
        order_by = config.DEFAULT_ORDER

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
    is_secret = bool(request.form.get("secret"))

    if (len(title) < 1 or len(title) > 30 or
        all(re.search("^[ZC]", unicodedata.category(c)) for c in title) or
        len(desc) < 1 or len(desc) > 100):
        return redirect(url_for("forums"))

    subforums.new_subforum(title, desc, is_secret)

    return redirect(url_for("forums"))

@app.route("/subforum/edit/<int:subforum_id>")
def edit_subforum(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    permitted = permissions.get_permitted_users(subforum_id)
    blocked = permissions.get_blocked_users(subforum_id)

    return render_template("edit_subforum.html", subforum_id=subforum_id,
                           permitted_users=permitted, blocked_users=blocked)

@app.route("/subforum/delete/<int:subforum_id>", methods=["POST"])
def delete_subforum(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    subforums.delete_subforum(subforum_id)

    return redirect(url_for("forums"))

@app.route("/thread/<int:thr_id>")
def thread(thr_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    thr = threads.get_thr(thr_id)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        return redirect(url_for("forums"))

    order_by = request.args.get("order_by")
    if order_by not in ["newest", "oldest", "most_liked", "most_disliked"]:
        order_by = config.DEFAULT_ORDER

    user = users.get_user(session["username"])
    msgs = messages.get_tree(thr.first_msg, user.id, order_by)
    first_msg = next(msg for msg in msgs if msg.id == thr.first_msg)

    return render_template("thread.html", thread=thr, msgs=msgs,
                           first_msg=first_msg, order_by=order_by,
                           is_admin=user.admin)

@app.route("/thread/new/<int:subforum_id>")
def new_thr(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if not subforums.is_permitted(subforum_id, session["username"]):
        return redirect(url_for("forums"))

    return render_template("new_thread.html", subforum_id=subforum_id)

@app.route("/thread/create/<int:subforum_id>", methods=["POST"])
def create_thr(subforum_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not subforums.is_permitted(subforum_id, session["username"]):
        return redirect(url_for("forums"))

    title = request.form["title"]
    msg = request.form["message"]

    if (len(title) < 1 or len(title) > 30 or len(msg) < 1 or len(msg) > 100 or
        all(re.search("^[ZC]", unicodedata.category(c)) for c in title)):
        return redirect(url_for("new_thr", subforum_id=subforum_id))

    thr_id = threads.new_thr(users.get_user(session["username"]).id,
                             subforum_id, title, msg)

    return redirect(url_for("thread", thr_id=thr_id))

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

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    is_admin = users.is_admin(session["username"])
    thr = threads.get_thr(thr_id)

    if session["username"] != thr.username and not is_admin:
        return redirect(url_for("thread", thr_id=thr_id))

    title = request.form["title"]

    if len(title) < 1 or len(title) > 30:
        return redirect(url_for("edit_thr", thr_id=thr_id))

    threads.edit_thr(thr_id, title)

    return redirect(url_for("thread", thr_id=thr_id))

@app.route("/thread/delete/<int:thr_id>", methods=["POST"])
def delete_thr(thr_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

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

    thr = threads.get_thr(messages.get_msg(msg_id).thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        return redirect(url_for("forums"))

    return render_template("new_message.html", msg_id=msg_id, thr_id=thr.id)

@app.route("/send/<int:orig_id>", methods=["POST"])
def send(orig_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    thr = threads.get_thr(messages.get_msg(orig_id).thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        return redirect(url_for("forums"))

    content = request.form["content"]

    if len(content) < 1 or len(content) > 100:
        return redirect(url_for("message", msg_id=orig_id))

    user = users.get_user(session["username"])
    messages.new_msg(orig_id, user.id, thr.id, content)

    return redirect(url_for("thread", thr_id=thr.id))

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

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    user = users.get_user(session["username"])
    msg = messages.get_msg(msg_id)

    if user.id != msg.uid and not user.admin:
        return redirect(url_for("thread", thr_id=msg.thread))

    content = request.form["content"]

    if len(content) < 1 or len(content) > 100:
        return redirect(url_for("edit", msg_id=msg_id))

    messages.edit_msg(msg_id, content)

    return redirect(url_for("thread", thr_id=msg.thread))

@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    msg = messages.get_msg(msg_id)

    cur_user = users.get_user(session["username"])
    if msg.uid != cur_user.id and not users.is_admin(session["username"]):
        return redirect(url_for("thread", thr_id=msg.thread))

    subforum_id = threads.get_thr(msg.thread).subforum

    messages.delete_msg(msg_id)

    if not threads.get_thr(msg.thread):
        return redirect(url_for("subforum", subforum_id=subforum_id))

    return redirect(url_for("thread", thr_id=msg.thread))

@app.route("/permission/add", methods=["POST"])
def add_permission():
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    uid = int(request.form["uid"])
    subforum_id = request.form["subforum"]

    if users.is_admin(uid) or not subforums.get_subforum(subforum_id).secret:
        return redirect(url_for("forums"))

    permissions.add_permission(uid, subforum_id)

    return redirect(url_for("edit_subforum", subforum_id=subforum_id))

@app.route("/permission/delete", methods=["POST"])
def delete_permission():
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    uid = request.form["uid"]
    subforum_id = request.form["subforum"]

    permissions.delete_permission(uid, subforum_id)

    return redirect(url_for("edit_subforum", subforum_id=subforum_id))

@app.route("/like/<int:msg_id>", methods=["POST"])
def like(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    thr = threads.get_thr(messages.get_msg(msg_id).thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        return redirect(url_for("forums"))

    likes.like(users.get_user(session["username"]).id, msg_id)

    return redirect(url_for("thread", thr_id=thr.id))

@app.route("/dislike/<int:msg_id>", methods=["POST"])
def dislike(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    thr = threads.get_thr(messages.get_msg(msg_id).thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        return redirect(url_for("forums"))

    likes.dislike(users.get_user(session["username"]).id, msg_id)

    return redirect(url_for("thread", thr_id=thr.id))

@app.route("/unlike/<int:msg_id>", methods=["POST"])
def unlike(msg_id):
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    thr = threads.get_thr(messages.get_msg(msg_id).thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        return redirect(url_for("forums"))

    likes.unlike(users.get_user(session["username"]).id, msg_id)

    return redirect(url_for("thread", thr_id=thr.id))

@app.route("/search", methods=["POST"])
def search():
    if "username" not in session:
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    search_term = request.form["search_term"]

    if len(search_term) < 1 or len(search_term) > 100:
        return redirect(url_for("forums"))

    results = messages.search(search_term, session["username"])

    return render_template("search_results.html", results=results)
