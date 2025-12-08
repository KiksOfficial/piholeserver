import os
from sys_performance import get_cpu_temp, get_ram_info
from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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

        return render_template("home.html",
                               cpu_temp=cpu_temp,
                               ram_used=ram_data['used_gb'],
                               ram_total=ram_data['total_gb'],
                               ram_percent=ram_data['percent'])
    # a simple page that says hello
    @app.route('/login-signup', methods=['Get', 'POST'])
    def login_signup():
        return render_template("login-signup.html)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

