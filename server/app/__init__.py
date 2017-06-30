from flask import Flask
from flask_mongoengine import MongoEngine
from flask_principal import Principal 
import threading
import os, time

db = MongoEngine()
principals = Principal()
lock = threading.Condition()

def create_app(config_name):
    from .config import config
    from main.urls import main
    from main.models import Models

    app = Flask(__name__, 
        template_folder=config[config_name].TEMPLATE_PATH, static_folder=config[config_name].STATIC_PATH)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    db.init_app(app)
    Models().load_data()

    principals.init_app(app)

    app.register_blueprint(main)

    return app

class Loop(threading.Thread):
    def __init__(self, lock):
        self._lock = lock
        threading.Thread.__init__(self)
 
    def run(self):
        while True:
            if self._lock.acquire():
                self.tick()
                self._lock.release()
            time.sleep(60)

    def tick(self):
        from main.models import Models
        Models().add_data()

app = create_app(os.getenv('config') or 'prd')

l = Loop(lock)
l.setDaemon(True)
l.start()