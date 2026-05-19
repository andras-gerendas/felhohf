import configparser
from flask import Flask
import os

def load_config_as_dict(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    config_dict = {}
    for section in config.sections():
        config_dict[section] = {key.upper(): value for key, value in config.items(section)}

    return config_dict

def create_app():
    app = Flask(__name__)

    config_path = os.environ.get("FLASK_CONFIG_PATH")

    if not os.path.isfile(config_path):
        raise Exception("Config not found", config_path)
    
    app.config.update(load_config_as_dict(config_path))

    app.config.from_mapping(SECRET_KEY=app.config["FLASK"]["SECRET_KEY"])

    from . import gallery
    app.register_blueprint(gallery.bp)

    app.add_url_rule("/", endpoint="index")

    return app