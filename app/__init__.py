#!./bl-env/bin/python
from os import path
import sys

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config="True")
    app.config.from_object(app.config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    return app
