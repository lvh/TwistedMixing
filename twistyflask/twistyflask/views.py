from flask import render_template
from twistyflask import app

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
    return render_template("chat.html", title=u"chat channel")
