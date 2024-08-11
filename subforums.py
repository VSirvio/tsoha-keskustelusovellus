from sqlalchemy.sql import text
from db import db

def get_subforums():
    sql = text(
        "SELECT F.id, F.title, F.description,"
        " COUNT(DISTINCT T.id) AS threads,"
        " COUNT(M.id) AS messages,"
        " TO_CHAR(MAX(M.sent), 'DD.MM.YYYY klo HH24:MI') AS latest "
        "FROM subforums F "
        "LEFT JOIN threads T ON F.id = T.subforum "
        "LEFT JOIN messages M ON T.id = M.thread "
        "GROUP BY F.id ORDER BY F.id"
    )
    return db.session.execute(sql).fetchall()

def get_subforum(subforum_id : int):
    sql = text("SELECT title, description FROM subforums WHERE id = :id")
    return db.session.execute(sql, {"id": subforum_id}).fetchone()

def delete_subforum(subforum_id : int):
    sql = text("DELETE FROM subforums WHERE id = :id")
    db.session.execute(sql, {"id": subforum_id})
    db.session.commit()
