"""Retrieve tweets, embeddings, and persist in database"""
import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User # , Follower

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))

def get_user(username):
    return TWITTER.get_user(username)

# def get_followers(username, twitter_user):

#     try:
#         followers = TWITTER.followers(username)
#         print('looping through followers')
#         for f in followers:
#             print(f.screen_name)
#             db_follower = Follower(f.id,
#                                    user_id=twitter_user.id,
    #                                follower_name=f.screen_name)
    #         DB.session.add(db_follower)
    #     print('finished looping through followers')
    # except Exception as e:
    #     print('Error processing {}: {}'.format(username, e))
    #     raise e
    # else: # If there is no error, do this.
    #     print('commiting session')
    #     DB.session.commit()
    # print('Got followers')

def add_or_update_user(username):
    """Add or update a user and their tweets, error if no/private user."""
    try:
        twitter_user = TWITTER.get_user(username)

        db_user = User.query.get(twitter_user.id)
        if db_user == None:
            db_user = User(id=twitter_user.id, name=username)
            DB.session.add(db_user)
            # get_followers(username, twitter_user)

        # We want as many recent non-retweet/reply statuses as we can get
        tweets = twitter_user.timeline(
            count=200,
            exclude_replies=True,    # Want only original tweets - not replies.
            include_rts=False,       # We don't want retweets.
            tweet_mode='extended',   # The full_text attribute contains at most
                                     # 280 characters. The text attribute contains
                                     # at most 140 characters. The extended tweet
                                     # mode allows full_text attrib to be 280 chars.
            since_id=db_user.newest_tweet_id)  # Since the last tweet we received
                                               # from this user.
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        for tweet in tweets:
            # Get embedding for tweet, and store in db
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:500],
                             embedding=embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e
    else: # If there is no error, do this.
        DB.session.commit()

# TODO write some useful functions
