from sqlalchemy.sql import text
from db import db

def get_user(username : str):
    sql = text(
        "SELECT id, password, admin FROM users WHERE username = :username"
    )
    return db.session.execute(sql, {"username": username}).fetchone()

def is_admin(username : str):
    sql = text("SELECT admin FROM users WHERE username = :username")
    return db.session.execute(sql, {"username": username}).fetchone().admin

def register(username : str, password : str):
    sql = text(
        "INSERT INTO users (username, password) VALUES (:username, :password)"
    )
    db.session.execute(sql, {"username": username, "password": password})
    db.session.commit()
