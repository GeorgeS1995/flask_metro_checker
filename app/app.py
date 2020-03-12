from flask import Flask
from .configuration import Configuration
from flask_sqlalchemy import SQLAlchemy

# create and configure the app
app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)
