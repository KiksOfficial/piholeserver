import os
from python_files.sys_performance import get_cpu_temp, get_ram_info, get_cpu_usage
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, abort, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from python_files.forms import LoginForm
from python_files.upload_download_files import Upload
from urllib.parse import urlparse, urljoin
from extensions import db
from io import BytesIO

login_manager = LoginManager()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    db_path = os.path.join(app.instance_path, 'project.sqlite3')

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    login_manager.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
     
    def is_safe_url(target):
        host_url = urlparse(request.host_url)
        redirect_url = urlparse(urljoin(request.host_url, target))
        return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc
    
    @app.route('/logout')
    def logout():
        logout_user()
        flash('Logged out')
        return redirect(url_for('login'))

    @app.route('/', methods = ['GET', 'POST'])
    @login_required
    def home():
        if request.method == 'POST':
            file = request.files['file']
            upload = Upload(filename=file.filename, data=file.read())
            db.session.add(upload)
            db.session.commit()

            return f'Uploaded: {file.filename}'
        
        cpu_temp = get_cpu_temp()
        ram_data = get_ram_info()
        cpu_usage = get_cpu_usage()

        return render_template("home.html",
                               cpu_temp=cpu_temp,
                               ram_used=ram_data['used_gb'],
                               ram_total=ram_data['total_gb'],
                               ram_percent=ram_data['percent'],
                               cpu_usage=cpu_usage)
    class User(UserMixin):
            users = {'admin': {'id':'1', 'password':'admin'}}
            
            def __init__(self, username):
                self.username = username
                self.id = self.users[username]['id']
                self.password = self.users[username]['password']

            @classmethod
            def get(cls, username):
                user_data = cls.users.get(username)
                if user_data:
                    user = cls(username)
                    return user
                return None
            @classmethod
            def get_by_id(cls, user_id):
                for username, data in cls.users.items():
                    if data['id'] == user_id:
                        return cls(username)
                return None


    @app.route('/login', methods=['GET', 'POST'])
    def login():
# Here we use a class of some kind to represent and validate our
# client-side form data. For example, WTForms is a library that will
# handle this for us, and we use a custom LoginForm to validate.
        form = LoginForm()
        if form.validate_on_submit():
            user = User.get(form.username.data)
            # Login and validate the user.
            # user should be an instance of your `User` class
            
            if user and user.password == form.password.data:
                flash('logged in successfully')
                login_user(user)

                next_page = request.args.get('next')
                if next_page and not is_safe_url(next_page):
                    return abort(400)
                return redirect(next_page or url_for('home'))
            else:
                flash('Invalid credentials')

           
        return render_template('login.html', form=form)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    @app.route('/api/stats')
    @login_required
    def api_stats():
        cpu_temp = get_cpu_temp()
        ram_data = get_ram_info()
        cpu_usage = get_cpu_usage()

        return jsonify({
            "cpu_temp": cpu_temp,
            "ram_used": ram_data['used_gb'],
            "ram_total": ram_data['total_gb'],
            "ram_percent": ram_data['percent'],
            "cpu_usage": cpu_usage,
        })

    @app.route('/download/<upload_id>')
    def download(upload_id):
        upload = Upload.query.filter_by(id=upload_id).first()
        return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0'', port=5000)

