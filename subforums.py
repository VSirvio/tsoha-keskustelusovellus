from sqlalchemy.sql import text
from db import db

def get_subforums():
    sql = text("SELECT id, title, description FROM subforums")
    return db.session.execute(sql).fetchall()

def get_subforum(subforum_id : int):
    select_subforum = text(
        f"SELECT title, description FROM subforums WHERE id = {subforum_id}"
    )
    return db.session.execute(select_subforum).fetchone()
