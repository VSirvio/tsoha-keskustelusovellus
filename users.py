from sqlalchemy.sql import text
from db import db

def get_user(username : str):
    sql = text("SELECT id, password FROM users WHERE username = :username")
    return db.session.execute(sql, {"username": username}).fetchone()

def register(username : str, password : str):
    sql = text(
        "INSERT INTO users (username, password) VALUES (:username, :password)"
    )
    db.session.execute(sql, {"username": username, "password": password})
    db.session.commit()
