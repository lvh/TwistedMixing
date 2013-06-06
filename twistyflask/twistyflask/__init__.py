from axiom import store
from flask import Flask
from os import environ
from twistyflask._version import __version__; __version__ # shut up pyflakes

app = Flask("twistyflask")

def addStore(_environ=environ):
    """
    Gets a store path from the environment. If unset, creates in-memory store.
    """
    app.store = store.Store(_environ.get("STORE_PATH"))

addStore()

from twistyflask import views; views # shut up pyflakes
