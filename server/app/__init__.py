import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_principal import Principal 

db = MongoEngine()
principals = Principal()

def create_app(config_name):
    from .config import config
    from main.urls import main
    from main import models

    app = Flask(__name__, 
        template_folder=config[config_name].TEMPLATE_PATH, static_folder=config[config_name].STATIC_PATH)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    db.init_app(app)
    models.load_data()

    principals.init_app(app)

    app.register_blueprint(main)

    return app

app = create_app(os.getenv('config') or 'prd')