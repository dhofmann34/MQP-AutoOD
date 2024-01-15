import uuid

from autoOD.home import home_bp
from connect import create_session_run_tables, new_session
from flask import session, redirect


@home_bp.route('/', methods=['GET', 'POST'])
def home():
    create_session_run_tables
    if 'user_id' in session:
        user_id = session['user_id']
        return redirect('/autood/index')
        # return f'Hello returning user! Your user ID is {user_id}'
    else:
        # If 'user_id' is not in the session, generate a new ID and store it
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        new_session(user_id)
        return redirect('/autood/index')
        # return f'Hello new user! Your user ID is {user_id}'
