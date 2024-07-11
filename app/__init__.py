from flask import Flask
from flask_bcrypt import Bcrypt

from models import db

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['CAMPAIGN_IMAGE'] = app.instance_path + '/media/campaign_images/'

    from .main import main_bp
    from .auth import auth_bp
    from .sponsor import sponsor_bp

    bcrypt.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(sponsor_bp)

    return app
