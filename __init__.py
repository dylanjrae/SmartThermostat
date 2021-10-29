from flask import Flask


mqtt = Mqtt()

def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.DevConfig')

    mqtt.init_app(app)

    with app.app_context():
        from . import routes