from flask import Flask
import os
import logging
import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings('ignore', category=NotOpenSSLWarning)

def create_app():
    app = Flask(__name__)

    from app.routes.base_routes import bp as base_bp
    app.register_blueprint(base_bp)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

    # Disable Flask development server logging
    app.logger.disabled = True
    logging.getLogger('werkzeug').disabled = True
    
    return app