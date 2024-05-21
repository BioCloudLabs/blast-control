import os
from flask import Flask
from flask_smorest import Api
from controllers.vm import blp as VmController
from dotenv import load_dotenv
import signal

app: Flask = Flask(__name__, static_folder="dist", static_url_path="/")

load_dotenv()

app.config["API_TITLE"] = os.getenv("API_TITLE")
app.config["API_VERSION"] = os.getenv("API_VERSION")
app.config["OPENAPI_VERSION"] = os.getenv("OPENAPI_VERSION")

api: Api = Api(app)

api.register_blueprint(VmController)

if __name__ == '__main__':
    from dockerize import stop_scheduler  
    
    signal.signal(signal.SIGINT, stop_scheduler)
    signal.signal(signal.SIGTERM, stop_scheduler)
    
    app.run(debug=True)