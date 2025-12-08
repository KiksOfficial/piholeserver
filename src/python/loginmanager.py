from flask_login import LoginManager
from . __init__ import app

login_manager = LoginManager()
login_manager.init_app(app)
