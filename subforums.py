from sqlalchemy.sql import text
from db import db
import config

def get_subforums(cur_username : str):
    sql = text(
        "SELECT F.id, F.title, F.description, F.secret,"
        " COUNT(DISTINCT T.id) AS threads,"
        " COUNT(M.id) AS messages,"
        " TO_CHAR(MAX(M.sent), :date_format) AS latest "
        "FROM subforums F "
        "LEFT JOIN users C ON C.username = :cur_username "
        "LEFT JOIN threads T ON F.id = T.subforum "
        "LEFT JOIN messages M ON T.id = M.thread "
        "LEFT JOIN permissions P ON P.uid = C.id AND P.subforum = F.id "
        "GROUP BY F.id, C.id HAVING admin OR COUNT(P.uid) > 0 OR NOT F.secret "
        "ORDER BY F.id"
    )
    params = {"date_format": config.DATE_FORMAT, "cur_username": cur_username}
    return db.session.execute(sql, params).fetchall()

def get_subforum(subforum_id : int):
    sql = text(
        "SELECT id, title, description, secret FROM subforums WHERE id = :id"
    )
    return db.session.execute(sql, {"id": subforum_id}).fetchone()

def is_permitted(subforum_id : int, username : str):
    sql = text(
        "SELECT (NOT F.secret) OR COUNT(P.uid) > 0 OR U.admin AS is_permitted "
        "FROM subforums F "
        "LEFT JOIN users U ON U.username = :username "
        "LEFT JOIN permissions P ON P.uid = U.id AND P.subforum = F.id "
        "WHERE F.id = :subforum "
        "GROUP BY F.id, U.id"
    )
    params = {"username": username, "subforum": subforum_id}
    return db.session.execute(sql, params).fetchone().is_permitted

def new_subforum(title : str, desc : str, is_secret : bool):
    sql = text(
        "INSERT INTO subforums (title, description, secret)"
        " VALUES (:title, :desc, :is_secret)"
    )
    params = {"title": title, "desc": desc, "is_secret": is_secret}
    db.session.execute(sql, params)
    db.session.commit()

def delete_subforum(subforum_id : int):
    sql = text("DELETE FROM subforums WHERE id = :id")
    db.session.execute(sql, {"id": subforum_id})
    db.session.commit()
