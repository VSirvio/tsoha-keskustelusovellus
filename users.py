from sqlalchemy.sql import text
from db import db

def get_user(username : str):
    sql = text("SELECT id, password FROM users WHERE username = :username")
    return db.session.execute(sql, {"username": username}).fetchone()
