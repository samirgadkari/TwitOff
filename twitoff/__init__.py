"""Entry point for TwitOff flask application."""

# Since we're inside twitoff, we can
# use .app instead of twitoff.app here
from .app import create_app

APP = create_app()
