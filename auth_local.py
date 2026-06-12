import uuid
from datetime import datetime, timedelta
from db_local import get_conn


def create_session(username):
    token = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(days=1)
    c = get_conn()
    cur = c.cursor()
    cur.execute('DELETE FROM sessions WHERE "expiry" < GETDATE()')
    cur.execute(
        'INSERT INTO sessions ("token","username","expiry") VALUES (?,?,?)',
        (token, username, expiry)
    )
    c.commit()
    c.close()
    return token


def validate_session(token):
    if not token:
        return None
    c = get_conn()
    cur = c.cursor()
    cur.execute(
        'SELECT "username" FROM sessions WHERE "token"=? AND "expiry" > GETDATE()',
        (token,)
    )
    row = cur.fetchone()
    c.close()
    return row[0] if row else None


def delete_session(token):
    if not token:
        return
    c = get_conn()
    cur = c.cursor()
    cur.execute('DELETE FROM sessions WHERE "token"=?', (token,))
    c.commit()
    c.close()
