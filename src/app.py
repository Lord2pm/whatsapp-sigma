from flask import Flask

from .config import Config
from .controllers import whatsapp_controller, home_controller


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(home_controller.home_controller)
app.register_blueprint(whatsapp_controller.whatsapp_controller)
