import re
import secrets

from flask import abort, flash, redirect, render_template, \
                  request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

import config
import likes
import messages
import permissions
import subforums
import threads
import users
from app import app
from utils import is_printable, nonprintable_chars_to_whitespace

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

    if len(username) > 30 or len(password) > 30:
        flash("Invalid login info")
        return redirect(url_for("signin"))

    user = users.get_user(username)

    if (not user) or (not check_password_hash(user.password, password)):
        flash("Invalid login info")
        return redirect(url_for("signin"))

    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    session["prev_order"] = {}

    return redirect(url_for("forums"))

@app.route("/logout", methods=["POST"])
def logout():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    del session["username"]
    del session["csrf_token"]
    del session["prev_order"]

    return redirect(url_for("signin"))

@app.route("/registration")
def registration():
    if "username" in session:
        return redirect(url_for("forums"))
    return render_template("registration.html",
                           username_pattern=config.ALLOWED_USERNAME_PATTERN)

@app.route("/register", methods=["POST"])
def register():
    if "username" in session:
        return redirect(url_for("forums"))

    username = request.form["username"]
    password = request.form["password"]
    password2 = request.form["password2"]

    error = False

    if (len(username) < 5 or len(username) > 30
        or not re.fullmatch(config.ALLOWED_USERNAME_PATTERN, username)):
        flash("Invalid username")
        error = True

    if len(password) < 5 or len(password) > 30:
        flash("Invalid password")
        error = True

    if password != password2:
        flash("Passwords not matching")
        error = True

    if users.get_user(username):
        flash("Username already in use")
        error = True

    if error:
        return redirect(url_for("registration"))

    users.register(username, generate_password_hash(password))

    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    session["prev_order"] = {}

    return redirect(url_for("forums"))

@app.route("/forums")
def forums():
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    forum_list = subforums.get_subforums(session["username"])

    return render_template("subforum_list.html", subforums=forum_list,
                           is_admin=users.is_admin(session["username"]))

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    cur_subforum = subforums.get_subforum(subforum_id)

    if not cur_subforum:
        flash("Kyseistä keskustelualuetta ei ole olemassa")
        return redirect(url_for("forums"))

    if not subforums.is_permitted(subforum_id, session["username"]):
        flash("Ei pääsyoikeutta kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    order_by = request.args.get("order_by")
    if order_by not in ["newest", "oldest", "most_liked", "most_disliked"]:
        order_by = config.DEFAULT_ORDER

    thrs = threads.get_thrs(subforum_id, order_by)

    return render_template("subforum.html", subforum=cur_subforum, thrs=thrs,
                           is_admin=users.is_admin(session["username"]),
                           order_by=order_by)

@app.route("/subforum/new")
def new_subforum():
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if not users.is_admin(session["username"]):
        flash(config.ADMIN_USER_REQUIRED_MSG)
        return redirect(url_for("forums"))

    return render_template("new_subforum.html")

@app.route("/subforum/create", methods=["POST"])
def create_subforum():
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not users.is_admin(session["username"]):
        flash(config.ADMIN_USER_REQUIRED_MSG)
        return redirect(url_for("forums"))

    title = request.form["title"]
    desc = request.form["description"]
    is_secret = bool(request.form.get("secret"))

    error = False

    if (len(title) < 1 or len(title) > 30
        or all(not is_printable(char) for char in title)):
        flash("Invalid title")
        error = True

    if (len(desc) < 1 or len(desc) > 100
        or all(not is_printable(char) for char in desc)):
        flash("Invalid description")
        error = True

    if error:
        return redirect(url_for("new_subforum"))

    title = nonprintable_chars_to_whitespace(title)
    desc = nonprintable_chars_to_whitespace(desc)

    subforums.new_subforum(title, desc, is_secret)

    return redirect(url_for("forums"))

@app.route("/subforum/edit/<int:subforum_id>")
def edit_subforum(subforum_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if not subforums.get_subforum(subforum_id):
        flash("Kyseistä keskustelualuetta ei ole olemassa")
        return redirect(url_for("forums"))

    if not users.is_admin(session["username"]):
        flash(config.ADMIN_USER_REQUIRED_MSG)
        return redirect(url_for("forums"))

    permitted = permissions.get_permitted_users(subforum_id)
    blocked = permissions.get_blocked_users(subforum_id)

    return render_template("edit_subforum.html", subforum_id=subforum_id,
                           permitted_users=permitted, blocked_users=blocked)

@app.route("/subforum/delete/<int:subforum_id>", methods=["POST"])
def delete_subforum(subforum_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not subforums.get_subforum(subforum_id):
        flash("Kyseistä keskustelualuetta ei ole olemassa")
        return redirect(url_for("forums"))

    if not users.is_admin(session["username"]):
        return redirect(url_for("forums"))

    subforums.delete_subforum(subforum_id)

    return redirect(url_for("forums"))

@app.route("/thread/<int:thr_id>")
def thread(thr_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    thr = threads.get_thr(thr_id)

    if not thr:
        flash("Kyseistä keskustelua ei ole olemassa")
        return redirect(url_for("forums"))

    if not subforums.is_permitted(thr.subforum, session["username"]):
        flash("Ei pääsyoikeutta kyseiseen keskusteluun")
        return redirect(url_for("forums"))

    order_by = request.args.get("order_by")
    if order_by not in ["newest", "oldest", "most_liked", "most_disliked"]:
        if "prev_order" in session and str(thr_id) in session["prev_order"]:
            order_by = session["prev_order"][str(thr_id)]
        else:
            order_by = config.DEFAULT_ORDER

    session["prev_order"][str(thr_id)] = order_by
    session.modified = True

    user = users.get_user(session["username"])
    msgs = messages.get_tree(thr.first_msg, user.id, order_by)
    first_msg = next(msg for msg in msgs if msg.id == thr.first_msg)

    return render_template("thread.html", thread=thr, msgs=msgs,
                           first_msg=first_msg, order_by=order_by,
                           is_admin=user.admin)

@app.route("/thread/new/<int:subforum_id>")
def new_thr(subforum_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if not subforums.get_subforum(subforum_id):
        flash("Kyseistä keskustelualuetta ei ole olemassa")
        return redirect(url_for("forums"))

    if not subforums.is_permitted(subforum_id, session["username"]):
        flash("Ei pääsyoikeutta kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    return render_template("new_thread.html", subforum_id=subforum_id)

@app.route("/thread/create/<int:subforum_id>", methods=["POST"])
def create_thr(subforum_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not subforums.get_subforum(subforum_id):
        flash("Kyseistä keskustelualuetta ei ole olemassa")
        return redirect(url_for("forums"))

    if not subforums.is_permitted(subforum_id, session["username"]):
        flash("Ei pääsyoikeutta kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    title = request.form["title"]
    msg = request.form["message"]

    error = False

    if (len(title) < 1 or len(title) > 30
        or all(not is_printable(char) for char in title)):
        flash("Invalid title")
        error = True

    if len(msg) < 1 or len(msg) > 100:
        flash("Invalid message")
        error = True

    if error:
        return redirect(url_for("new_thr", subforum_id=subforum_id))

    title = nonprintable_chars_to_whitespace(title)

    thr_id = threads.new_thr(users.get_user(session["username"]).id,
                             subforum_id, title, msg)

    return redirect(url_for("thread", thr_id=thr_id))

@app.route("/thread/edit/<int:thr_id>")
def edit_thr(thr_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    thr = threads.get_thr(thr_id)

    if not thr:
        flash("Kyseistä keskustelua ei ole olemassa")
        return redirect(url_for("forums"))

    is_admin = users.is_admin(session["username"])

    if session["username"] != thr.username and not is_admin:
        flash("Ei muokkausoikeutta kyseiseen keskusteluun")
        return redirect(url_for("forums"))

    return render_template("edit_thread.html", thr=thr)

@app.route("/thread/save/<int:thr_id>", methods=["POST"])
def save_thr(thr_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    thr = threads.get_thr(thr_id)

    if not thr:
        flash("Kyseistä keskustelua ei ole olemassa")
        return redirect(url_for("forums"))

    is_admin = users.is_admin(session["username"])

    if session["username"] != thr.username and not is_admin:
        flash("Ei muokkausoikeutta kyseiseen keskusteluun")
        return redirect(url_for("forums"))

    title = request.form["title"]

    if (len(title) < 1 or len(title) > 30
        or all(not is_printable(char) for char in title)):
        flash("Invalid title")
        return redirect(url_for("edit_thr", thr_id=thr_id))

    title = nonprintable_chars_to_whitespace(title)

    threads.edit_thr(thr_id, title)

    return redirect(url_for("thread", thr_id=thr_id))

@app.route("/thread/delete/<int:thr_id>", methods=["POST"])
def delete_thr(thr_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    thr = threads.get_thr(thr_id)

    if not thr:
        flash("Kyseistä keskustelua ei ole olemassa")
        return redirect(url_for("forums"))

    is_admin = users.is_admin(session["username"])

    if session["username"] != thr.username and not is_admin:
        flash("Ei muokkausoikeutta kyseiseen keskusteluun")
        return redirect(url_for("forums"))

    threads.delete_thr(thr_id)

    return redirect(url_for("subforum", subforum_id=thr.subforum))

@app.route("/reply/<int:msg_id>")
def message(msg_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    msg = messages.get_msg(msg_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    thr = threads.get_thr(msg.thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        flash("Ei pääsyoikeutta kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    return render_template("new_message.html", msg_id=msg_id, thr_id=thr.id)

@app.route("/send/<int:orig_id>", methods=["POST"])
def send(orig_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    msg = messages.get_msg(orig_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    thr = threads.get_thr(msg.thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        flash("Ei pääsyoikeutta kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    content = request.form["content"]

    if len(content) < 1 or len(content) > 100:
        flash("Invalid message")
        return redirect(url_for("message", msg_id=orig_id))

    user = users.get_user(session["username"])
    messages.new_msg(orig_id, user.id, thr.id, content)

    return redirect(url_for("thread", thr_id=thr.id))

@app.route("/edit/<int:msg_id>")
def edit(msg_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    msg = messages.get_msg(msg_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    user = users.get_user(session["username"])

    if user.id != msg.uid and not user.admin:
        flash("Ei muokkausoikeutta kyseiseen viestiin")
        return redirect(url_for("forums"))

    return render_template("edit_message.html", msg=msg)

@app.route("/save/<int:msg_id>", methods=["POST"])
def save(msg_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    msg = messages.get_msg(msg_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    user = users.get_user(session["username"])

    if user.id != msg.uid and not user.admin:
        flash("Ei muokkausoikeutta kyseiseen viestiin")
        return redirect(url_for("forums"))

    content = request.form["content"]

    if len(content) < 1 or len(content) > 100:
        flash("Invalid content")
        return redirect(url_for("edit", msg_id=msg_id))

    messages.edit_msg(msg_id, content)

    return redirect(url_for("thread", thr_id=msg.thread))

@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete(msg_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    msg = messages.get_msg(msg_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    cur_user = users.get_user(session["username"])

    if msg.uid != cur_user.id and not users.is_admin(session["username"]):
        flash("Ei muokkausoikeutta kyseiseen viestiin")
        return redirect(url_for("forums"))

    subforum_id = threads.get_thr(msg.thread).subforum

    messages.delete_msg(msg_id)

    if not threads.get_thr(msg.thread):
        return redirect(url_for("subforum", subforum_id=subforum_id))

    return redirect(url_for("thread", thr_id=msg.thread))

@app.route("/permission/add", methods=["POST"])
def add_permission():
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not users.is_admin(session["username"]):
        flash(config.ADMIN_USER_REQUIRED_MSG)
        return redirect(url_for("forums"))

    uid = int(request.form["uid"])
    subforum_id = request.form["subforum"]
    subforum_data = subforums.get_subforum(subforum_id)

    if not subforum_data:
        flash("Kyseistä keskustelualuetta ei ole olemassa")
        return redirect(url_for("forums"))

    if not users.exist(uid):
        flash("Kyseistä käyttäjää ei ole olemassa")
        return redirect(url_for("forums"))

    if users.is_admin(uid):
        flash("Pääkäyttäjillä on jo pääsyoikeus kaikille keskustelualueille")
        return redirect(url_for("forums"))

    if not subforum_data.secret:
        flash("Kyseinen keskustelualue on jo auki kaikille")
        return redirect(url_for("forums"))

    permissions.add_permission(uid, subforum_id)

    return redirect(url_for("edit_subforum", subforum_id=subforum_id))

@app.route("/permission/delete", methods=["POST"])
def delete_permission():
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not users.is_admin(session["username"]):
        flash(config.ADMIN_USER_REQUIRED_MSG)
        return redirect(url_for("forums"))

    uid = request.form["uid"]
    subforum_id = request.form["subforum"]

    permissions.delete_permission(uid, subforum_id)

    return redirect(url_for("edit_subforum", subforum_id=subforum_id))

@app.route("/like/<int:msg_id>", methods=["POST"])
def like(msg_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    msg = messages.get_msg(msg_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    thr = threads.get_thr(msg.thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        flash("Ei pääsyä kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    likes.like(users.get_user(session["username"]).id, msg_id)

    return redirect(url_for("thread", thr_id=thr.id))

@app.route("/dislike/<int:msg_id>", methods=["POST"])
def dislike(msg_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    msg = messages.get_msg(msg_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    thr = threads.get_thr(msg.thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        flash("Ei pääsyä kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    likes.dislike(users.get_user(session["username"]).id, msg_id)

    return redirect(url_for("thread", thr_id=thr.id))

@app.route("/unlike/<int:msg_id>", methods=["POST"])
def unlike(msg_id):
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    msg = messages.get_msg(msg_id)

    if not msg:
        flash("Kyseistä viestiä ei ole olemassa")
        return redirect(url_for("forums"))

    thr = threads.get_thr(msg.thread)

    if not subforums.is_permitted(thr.subforum, session["username"]):
        flash("Ei pääsyä kyseiselle keskustelualueelle")
        return redirect(url_for("forums"))

    likes.unlike(users.get_user(session["username"]).id, msg_id)

    return redirect(url_for("thread", thr_id=thr.id))

@app.route("/search", methods=["POST"])
def search():
    if "username" not in session:
        flash(config.LOGIN_REQUIRED_MSG)
        return redirect(url_for("signin"))

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    search_term = request.form["search_term"]

    if len(search_term) < 1 or len(search_term) > 100:
        flash("Invalid search term")
        return redirect(url_for("forums"))

    results = messages.search(search_term, session["username"])

    return render_template("search_results.html", results=results)
