"""Main application and logic for TwitOff"""
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import get_user

def create_app():
    """Create and configure and instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['ENV'] = config('ENV')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB Reset!', users=[])

    @app.route('/followers/<username>')
    def followers(username):
        user = get_user(username)

        res = username + "'s followers:<hr><ul>"
        for f in user.followers():
            res += "<li>" + f.screen_name + "</li>"
        res += "</ul"

        return res

    return app
