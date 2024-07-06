from flask import redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from app import create_app
from models import User

app = create_app()
app.config['SECRET_KEY'] = '9nL2hZpiJNzXUfneHq1RdhAu8A1vb9xd'
app.config['TEMPLATES_AUTO_RELOAD'] = True

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run()
