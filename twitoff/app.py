"""Main application and logic for TwitOff"""
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .predict import predict_user
from .twitter import get_followers, add_or_update_user, get_followers_from_db

def create_app():
    """Create and configure and instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None):
        message = ''
        name = name or request.values['user_name']
        followers = None
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = 'User {} successfully added!'.format(name)
                followers = get_followers(name)
            else:
                followers = get_followers_from_db(name)
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []

        return render_template('user.html', title=name, tweets=tweets,
                               message=message, followers=followers)

    @app.route('/compare', methods=['POST'])
    def compare():
        user1, user2 = request.values['user1'], request.values['user2']
        if user1 == user2:
            return 'Cannot compare a user to themselves!'
        else:
            text = request.values['tweet_text']
            prediction = predict_user(user1, user2, text)
            res = ((user1 if prediction else user2) + """ is more likely
                               to have said '{}'""").format(text)
            return res

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB Reset!', users=[])

    @app.route('/followers/<username>')
    def followers(username):
        user = User.query.filter(User.name == username).first()
        if user == None:
            return render_template('/error.html',
                                   title=username,
                                   message='User' + username +
                                   'not in database')

        followers_of_user = Follower.query.filter(Follower.user_id == user.id)
        names = [f.follower_name for f in followers_of_user]
        return render_template('followers.html',
                               title=username,
                               message='Followers for ' + username + ':',
                               followers=names)

    return app
