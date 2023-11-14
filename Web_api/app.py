import json
import os
from flask import Flask, request, render_template, send_from_directory, session, redirect, url_for
import uuid
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import secrets
from Database.database_orm import Upload, User
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
logged = False


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')

    engine = create_engine(f'sqlite:///../Database/db/mydatabase.db', echo=True)
    Session = sessionmaker(bind=engine)
    session_db = Session()

    if email:
        user = session_db.query(User).filter_by(email=email).first()
    else:
        user = None

    session_db.close()

    if user:
        global logged
        session['user_id'] = user.id
        logged = True

    return redirect(url_for('get_home_page'))


@app.route('/logout', methods=['POST'])
def logout():
    global logged
    session.pop('user_id', None)
    logged = False
    return redirect(url_for('get_home_page'))


@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')

    engine = create_engine(f'sqlite:///../Database/db/mydatabase.db', echo=True)
    Session = sessionmaker(bind=engine)
    session_db = Session()

    if email:
        user = session_db.query(User).filter_by(email=email).first()
        if user is None:
            user = User(email=email)
            session_db.add(user)
            session_db.commit()
            session_db.refresh(user)
    else:
        user = None

    session_db.close()

    if user:
        global logged
        session['user_id'] = user.id
        logged = True

    return redirect(url_for('get_home_page'))


@app.route('/', methods=['GET'])
def get_home_page():
    return render_template('index.html', json_data={}, logged_in=logged)


@app.route('/', methods=['POST'])
def upload_file():
    """
    Upload a file to the server
    :return: a json with the uid of the file
    """

    if 'pptx-file' not in request.files:
        return 'No file part in the request.'

    file = request.files.get('pptx-file')

    if not file:
        return 'No file selected.'

    timestamp = time.time()

    secret_string = file.filename + str(timestamp)
    namespace = uuid.uuid4()
    uid = uuid.uuid5(namespace, secret_string)

    engine = create_engine(f'sqlite:///../Database/db/mydatabase.db', echo=True)
    Session = sessionmaker(bind=engine)
    session_db = Session()

    if logged:
        user = session_db.query(User).filter_by(id=session.get('user_id')).first()
    else:
        user = None

    upload = Upload(uid=str(uid), filename=file.filename,
                    upload_time=datetime.now(),
                    user=user)
    session_db.add(upload)
    session_db.commit()
    session_db.close()

    file.save(f'uploads/{uid}.pptx')

    return f'uid: {uid}'


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get status of a pptx file
    :return: a json with the status of the file
    """

    engine = create_engine(f'sqlite:///../Database/db/mydatabase.db', echo=True)
    Session = sessionmaker(bind=engine)
    session_db = Session()

    uid = request.args.get('uid')
    filename = request.args.get('filename')

    if uid:
        upload = session_db.query(Upload).filter_by(uid=str(uid)).first()
    else:
        user = session_db.query(User).filter_by(id=session.get('user_id')).first()
        upload = session_db.query(Upload).filter_by(user_id=user.id, filename=f"{filename}.pptx").first()
        if not upload:
            upload = session_db.query(Upload).filter_by(user_id=user.id, filename=filename).first()

    session_db.close()

    if not upload:
        # return make_response(jsonify({'status': 'not found'}), 404)
        #########################################################
        json_data = {"0": "This file was not found"}
        #########################################################

    elif not upload.status.value == 'done':
        explanation = None
        ############################################
        json_data = {"0": "This file was not processed"}
        ############################################
    else:
        file = open(f'./outputs/{upload.uid}.json', 'r')
        explanation = json.load(file)
        file.close()
        #########################################################################
        json_data = list(explanation)

        json_data = [item.replace('\n', '\\n') for item in json_data]
        json_data = [item.replace('"', '') for item in json_data]
        json_data = {str(index): value for index, value in enumerate(json_data)}
        #########################################################################

    """
    response_data = {
        "status": str(upload.status.value),
        "filename": str(upload.filename),
        "finish time": str(upload.finish_time),
        "explanation": explanation
    }
    """

    # return make_response(jsonify(response_data), 200)
    #############################################################################
    return render_template('index.html', json_data=json_data, logged_in=logged)
    #############################################################################


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)
