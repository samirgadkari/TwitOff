"""SQL alchemy models for TwitOff"""
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class User(DB.Model):
    """Twitter users that we pull and analyze tweets for."""
    id = DB.Column(DB.BigInteger, primary_key=True)

    # We need this id, but we don't know how to get the primary
    # key (the id above). Have to do more googling to find out.
    # Until then, create this column with the same id.
    user_id = DB.Column(DB.BigInteger, nullable=False)

    name = DB.Column(DB.String(15), nullable=False)
    newest_tweet_id = DB.Column(DB.BigInteger)

    def __repr__(self):
        return '<User {}>'.format(self.name)

class Tweet(DB.Model):
    """Tweets"""
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(500)) # Tweets can be big, so you will have some truncated tweets

    # Pickle is the package for serializing/deserializing things
    embedding = DB.Column(DB.PickleType, nullable=False)

    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return '<Tweet {}>'.format(self.text)

class Follower(DB.Model):
    """Followers of a user"""
    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('followers', lazy=True))

    name = DB.Column(DB.String(15), nullable=False)

    def __repr__(self):
        return '<Follower {}>'.format(self.name)
