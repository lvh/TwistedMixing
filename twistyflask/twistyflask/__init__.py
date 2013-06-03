from twistyflask._version import __version__

from flask import Flask
app = Flask("twistyflask")

from twistyflask import views
