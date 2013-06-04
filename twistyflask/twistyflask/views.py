from flask import render_template
from twistyflask import app, log

@app.route("/")
def index():
    """
    Renders the index page.
    """
    return render_template("index.html")


@app.route("/chat")
def chat():
    """
    Renders the chat channel.
    """
    E = log.LogEntry
    entries = app.store.query(E, sort=E.time.ascending)
    kwargs = {"title": u"chat channel", "entries": entries}
    return render_template("chat.html", **kwargs)
