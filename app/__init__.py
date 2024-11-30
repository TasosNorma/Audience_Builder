from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    from app.routes.base_route import bp as base_bp
    app.register_blueprint(base_bp)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    
    return app