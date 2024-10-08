from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def sponsor_required(f):
    """
    Decorator that checks if the current user is a sponsor.
    If the user is not a sponsor, it redirects them to the home page.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.user_type != 'sponsor':
            return redirect(url_for('main.home'))
        if current_user.flagged:
            flash('Your account has been flagged. Please contact support for more information.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def influencer_required(f):
    """
    Decorator that checks if the current user is a influencer.
    If the user is not a sponsor, it redirects them to the home page.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.user_type != 'influencer':
            return redirect(url_for('main.home'))
        if current_user.flagged:
            flash('Your account has been flagged. Please contact support for more information.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_required(f):
    """
    Decorator that checks if the current user is anonymous.
    If the user is not anonymous, it redirects them to the home page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator that checks if the current user is an admin.
    If the user is not a sponsor, it redirects them to the home page.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.user_type != 'admin':
            return redirect(url_for('main.home'))
        if current_user.flagged:
            flash('Your account has been flagged. Please contact support for more information.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function