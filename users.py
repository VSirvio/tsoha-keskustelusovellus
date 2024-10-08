from sqlalchemy.sql import text

from db import db

def exist(uid : int):
    sql = text("SELECT id FROM users WHERE id = :uid")
    return bool(db.session.execute(sql, {"uid": uid}).fetchone())

def get_user(username : str):
    sql = text(
        "SELECT id, password, admin FROM users WHERE username = :username"
    )
    return db.session.execute(sql, {"username": username}).fetchone()

def is_admin(user : str | int):
    if isinstance(user, int):
        sql = text("SELECT admin FROM users WHERE id = :user")
    else:
        sql = text("SELECT admin FROM users WHERE username = :user")

    return db.session.execute(sql, {"user": user}).fetchone().admin

def register(username : str, password : str):
    sql = text(
        "INSERT INTO users (username, password) VALUES (:username, :password)"
    )
    db.session.execute(sql, {"username": username, "password": password})
    db.session.commit()
