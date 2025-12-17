import os
from  python.sys_performance import get_cpu_temp, get_ram_info, get_cpu_usage
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from form import LoginForms

login_manager = LoginManager()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    login_manager.init_app(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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

    @app.route('/')
    def home():

        cpu_temp = get_cpu_temp()
        ram_data = get_ram_info()
        cpu_usage = get_cpu_usage()

        return render_template("home.html",
                               cpu_temp=cpu_temp,
                               ram_used=ram_data['used_gb'],
                               ram_total=ram_data['total_gb'],
                               ram_percent=ram_data['percent'],
                               cpu_usage=cpu_usage)
    @app.route('/login', methods=['GET', 'POST'])
    def login():
# Here we use a class of some kind to represent and validate our
# client-side form data. For example, WTForms is a library that will
# handle this for us, and we use a custom LoginForm to validate.
        form = LoginForm()
        if form.validate_on_submit():
            # Login and validate the user.
            # user should be an instance of your `User` class
            login_user(user)

            flask.flash('Logged in successfully.')

            next = flask.request.args.get('next')
            # url_has_allowed_host_and_scheme should check if the url is safe
            # for redirects, meaning it matches the request host.
            # See Django's url_has_allowed_host_and_scheme for an example.
            if not url_has_allowed_host_and_scheme(next, request.host):
                return flask.abort(400)

            return flask.redirect(next or flask.url_for('index'))
        return flask.render_template('login.html', form=form)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    @app.route('/api/stats')
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

    class Useer(UserMixin):
        users = {'admin': {'id':'1', 'password':'admin'}}

        @classmethod
        def get(cls, username):
            user_data = cls.get.users.get(username)
            if user_data:
                user.id = user_data['id']
                return user
            return None

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

