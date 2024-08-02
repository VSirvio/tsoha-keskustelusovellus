from sqlalchemy.sql import text
from db import db

def get_subforums():
    sql = text("SELECT id, title, description FROM subforums")
    return db.session.execute(sql).fetchall()

def get_subforum(subforum_id : int):
    sql = text("SELECT title, description FROM subforums WHERE id = :id")
    return db.session.execute(sql, {"id": subforum_id}).fetchone()
