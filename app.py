import os
import sys
from flask import Flask, jsonify, render_template, request, abort
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc

import speech_recognition as sr
from pydub import AudioSegment

from os import listdir
from os.path import isfile, join


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_script import Manager



#from forms import MusicSearchForm

from model import db, VideoFile, SearchForm, SortForm, User
# init flask app instance
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

# setup with the configuration provided by the user / environment
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['UPLOAD_EXTENSIONS'] = ['.webm','.mpg', '.mp2', '.mpeg', '.mpe', '.mpv','.ogg','.mp4', '.m4p', '.m4v','.avi', '.wmv','.mov', '.qt','.flv', '.swf','.avchd']
app.config['UPLOAD_PATH'] = 'static/video_files/'

# setup all our dependencies, for now only database using application factory pattern
db.init_app(app)
#manager = Manager(app)
migrate = Migrate(app, db)


#manager.add_command('db', MigrateCommand)





@app.route("/", methods=['GET', 'POST'])
def main_page():
    if not os.path.exists(app.config['UPLOAD_PATH']):
        init()

    column_sort = asc(VideoFile.id)
    sort = SortForm(request.form)
    if request.method == 'POST' and sort.data['select'] is not None:
        sort_string = sort.data['select']
        map_string_to_column = {'Date d\'ajout': desc(VideoFile.date_added),
                                'Nombre de lectures': desc(VideoFile.nb_lecture),
                                'Utilisateur': asc(VideoFile.user),
                                'Nom': asc(VideoFile.title)}
        column_sort = map_string_to_column[sort_string]

    items = VideoFile.query.order_by(column_sort).all()

    search = SearchForm(request.form)
    if request.method == 'POST' and search.data['search'] is not None:
        search_string = search.data['search'].lower()
        if search.data['search'] != '':
            items = [item for item in items if search_string in item.title.lower() or search_string in item.user.lower() or search_string in item.filename.lower() or search_string in str(item.transcription.lower())]


    return render_template('index.html', items=items, search_form=search, sort_form=sort)



@app.route("/upload/")
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        user_id = request.form.get('user id')

        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return 'id Discord inexistant'
        elif user.active is False:
            return 'id Discord banni'


        user = request.form.get('user')
        title = request.form.get('title')

        filename = request.files['file'].filename
        filename = filename.replace(' ','_')
        uploaded_file = request.files['file']
        byte_array = request.files['file'].read()
        request.files['file'].seek(0)

        if not os.path.exists(app.config['UPLOAD_PATH']):
            os.makedirs(app.config['UPLOAD_PATH'])

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        model = VideoFile(title=title, user=user, filename=filename, file=byte_array, user_id=user_id)
        db.session.add(model)
        db.session.commit()

        return 'file uploaded successfully'




@app.route('/count', methods = ['POST'])
def add_lecture_count():
    if request.method == 'POST':

        file_id = request.json['id']

        item = VideoFile.query.filter_by(id=file_id).first()
        item.nb_lecture = item.nb_lecture +1
        db.session.commit()

    return 'ok'





@app.route("/init")
def init():
    if not os.path.exists(app.config['UPLOAD_PATH']):
        os.makedirs(app.config['UPLOAD_PATH'])

    items = VideoFile.query.all()
    for item in items:
        file = open(app.config['UPLOAD_PATH']+item.filename, "wb")
        file.write(item.file)
        file.close()


    return 'init successfull'










@app.route("/stt")
def speech_to_text():
    r = sr.Recognizer()

    audio_files = VideoFile.query.filter(VideoFile.transcription.is_(None)).with_entities(VideoFile.filename).all()
    audio_files = [audio_file[0] for audio_file in audio_files]
    print(audio_files , file=sys.stderr)

    for audio_file in audio_files:
        file_ext = os.path.splitext(audio_file)[1]
        if file_ext == '.mp3':
            source, dest = join(app.config['UPLOAD_PATH'], audio_file), join(app.config['UPLOAD_PATH'], os.path.splitext(audio_file)[0]+'.wav')
            sound = AudioSegment.from_mp3(source)
            sound.export(dest, format="wav")
        else:
            dest = join(app.config['UPLOAD_PATH'], audio_file)


        with sr.VideoFile(dest) as audio_source:
            audio_data = r.record(audio_source)
            text = ''
            try:
                text = r.recognize_google(audio_data, language='fr-FR', pfilter=1, show_all=False)
            except:
                pass

            item = VideoFile.query.filter_by(filename=audio_file).first()
            item.transcription = text
            db.session.commit()
    return 'stt successfull'


if __name__ == "__main__":
    #manager.run()
    #db.create_all()

    db.create_all()
    db.session.commit()
    app.run()
