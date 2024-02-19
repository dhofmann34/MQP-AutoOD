import uuid
from application.home import home_bp
from connect import create_session_run_tables, new_session
from flask import session, redirect, render_template, current_app, send_file


@home_bp.route('/', methods=['GET', 'POST'])
def home():
    """Create a user ID tied to the user's browser session.
    User will use pre-existing ID if one exists.
    """
    create_session_run_tables()
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


@home_bp.route('/autood/about', methods=['GET'])
def about_form():
    return render_template('about.html')


@home_bp.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = current_app.config['DOWNLOAD_FOLDER'] + filename
    return send_file(file_path, as_attachment=False, attachment_filename='')
