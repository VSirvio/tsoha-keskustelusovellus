from sqlalchemy.sql import text
from db import db

def get_subforums():
    return db.session.execute(text("SELECT * FROM subforums")).fetchall()

def get_subforum(subforum_id : int):
    select_subforum = text(f"SELECT * FROM subforums WHERE id = {subforum_id}")
    return db.session.execute(select_subforum).fetchone()
