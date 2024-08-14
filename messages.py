from sqlalchemy.sql import text
from sqlalchemy.engine import Row
from db import db
import config

def get_msg(msg_id : int):
    sql = text(
        "SELECT M.id, M.content, M.thread, M.uid, U.username,"
        " TO_CHAR(M.sent, :date_format) AS time_str "
        "FROM messages M JOIN users U "
        "ON M.id = :msg_id AND U.id = M.uid"
    )
    params = {"date_format": config.DATE_FORMAT, "msg_id": msg_id}
    return db.session.execute(sql, params).fetchone()

def get_tree(root_msg : int, cur_user : int, order_by : str):
    order = "sent DESC"
    match order_by:
        case "oldest":
            order = "sent ASC"
        case "most_liked":
            order = "likes DESC"
        case "most_disliked":
            order = "likes ASC"

    sql = text(
        "SELECT M.id, M.content, U.username AS user, M.sent,"
        " TO_CHAR(M.sent, :date_format) AS time_str,"
        " COALESCE(SUM(L.value),0) AS likes,"
        " COUNT(I.value) > 0 AS liked,"
        " ARRAY_AGG(D.descendant) AS replies "
        "FROM message_tree_paths P "
        "LEFT JOIN messages M ON M.id = P.descendant "
        "LEFT JOIN users U ON U.id = M.uid "
        "LEFT JOIN likes L ON L.message = M.id "
        "LEFT JOIN likes I ON I.message = M.id AND I.uid = :cur_user "
        "LEFT JOIN message_tree_paths D ON D.ancestor = M.id AND D.depth = 1 "
        "WHERE P.ancestor = :root_msg "
        "GROUP BY M.id, U.username ORDER BY " + order
    )
    params = {
        "date_format": config.DATE_FORMAT,
        "cur_user": cur_user,
        "root_msg": root_msg
    }
    return db.session.execute(sql, params).fetchall()

def new_msg(orig_id : int, uid : int, thr_id : int, content : str):
    sql = text(
        "INSERT INTO messages "
        "(uid, thread, content) VALUES (:uid, :thr, :content) "
        "RETURNING id"
    )
    params = {"uid": uid, "thr": thr_id, "content": content}
    msg = db.session.execute(sql, params).fetchone()
    db.session.commit()

    sql = text(
        "INSERT INTO message_tree_paths "
        "(ancestor, descendant, depth) VALUES (:msg_id, :msg_id, 0)"
    )
    db.session.execute(sql, {"msg_id": msg.id})
    sql = text(
        "INSERT INTO message_tree_paths "
        "(ancestor, descendant, depth) "
        "SELECT ancestor, :msg_id, depth + 1"
        " FROM message_tree_paths"
        " WHERE descendant = :orig_id"
    )
    db.session.execute(sql, {"msg_id": msg.id, "orig_id": orig_id})
    db.session.commit()

    return msg.id

def edit_msg(msg_id : int, content : str):
    sql = text("UPDATE messages SET content = :content WHERE id = :id")
    db.session.execute(sql, {"content": content, "id": msg_id})
    db.session.commit()

def delete_msg(msg_id : int):
    sql = text(
        "DELETE FROM messages WHERE id IN ("
        " SELECT descendant FROM message_tree_paths WHERE ancestor = :msg_id"
        ")"
    )
    db.session.execute(sql, {"msg_id": msg_id})
    db.session.commit()

def search(search_terms : list[str], cur_user : Row):
    sql = text(
        "SELECT M.id, M.content, U.username, M.thread, T.title AS thr_title "
        "FROM messages M "
        "LEFT JOIN users U ON U.id = M.uid "
        "LEFT JOIN threads T ON T.id = M.thread "
        "LEFT JOIN subforums F ON F.id = T.subforum "
        "LEFT JOIN permissions P ON P.uid = :cur_user AND P.subforum = F.id "
        "WHERE regexp_split_to_array(lower(content), '\\W+') @> :search_terms "
        "GROUP BY M.id, U.id, T.id, F.id "
        "HAVING (NOT F.secret) OR :is_admin OR COUNT(P.uid) > 0"
    )
    params = {
        "cur_user": cur_user.id,
        "search_terms": search_terms,
        "is_admin": cur_user.admin
    }
    return db.session.execute(sql, params).fetchall()
