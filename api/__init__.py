from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#modifed to False if deploying with wsgi
app.debug = True

from app.mod_api.views import mod_api as api_module
from app.mod_onoff.views import mod_onoff as onoff_module

app.register_blueprint(api_module)
app.register_blueprint(onoff_module)

from app import views


