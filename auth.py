import uuid
import os
from datetime import datetime, timedelta

def _get_conn():
    import psycopg2
    import streamlit as st
    try:
        url = st.secrets["DATABASE_URL"]
    except Exception:
        url = os.environ.get("DATABASE_URL", "")
    return psycopg2.connect(url)


def create_session(username):
    token = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(days=1)
    c = _get_conn()
    cur = c.cursor()
    # clean expired sessions for this user while we're here
    cur.execute('DELETE FROM sessions WHERE "expiry" < NOW()')
    cur.execute(
        'INSERT INTO sessions ("token","username","expiry") VALUES (%s,%s,%s)',
        (token, username, expiry)
    )
    c.commit()
    c.close()
    return token


def validate_session(token):
    if not token:
        return None
    c = _get_conn()
    cur = c.cursor()
    cur.execute(
        'SELECT "username" FROM sessions WHERE "token"=%s AND "expiry" > NOW()',
        (token,)
    )
    row = cur.fetchone()
    c.close()
    return row[0] if row else None


def delete_session(token):
    if not token:
        return
    c = _get_conn()
    cur = c.cursor()
    cur.execute('DELETE FROM sessions WHERE "token"=%s', (token,))
    c.commit()
    c.close()


def restore_session():
    if st.session_state.get("logged_in"):
        return
    token = st.query_params.get("token")
    if token:
        username = validate_session(token)
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.token = token


def require_login():
    restore_session()
    if not st.session_state.get("logged_in"):
        st.switch_page("app.py")


def logout():
    token = st.session_state.get("token")
    if token:
        delete_session(token)
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.token = ""
    st.query_params.clear()
    st.switch_page("app.py")
