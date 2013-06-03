from lxml import html
from twistyflask import app
from unittest import TestCase


class _ViewTestCase(TestCase):
    """
    Common set up and tear down behavior for view tests.
    """
    def setUp(self):
        """
        Creates a test client, and puts the app in testing and debug mode.
        """
        self.client = app.test_client()
        app.testing = True
        app.debug = True

    def tearDown(self):
        """
        Turns the app's debug and testing modes off.
        """
        app.testing = False
        app.debug = False

class IndexTests(_ViewTestCase):
    def test_has_link_to_chat(self):
        """
        The index has a link to the chat page.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        link, = html.fromstring(response.data).cssselect("a[href$=chat]")
        self.assertIn("click here", link.text.lower())

class ChatTests(_ViewTestCase):
    def test_chat_in_title(self):
        """
        The chat view advertises itself in its title.
        """
        response = self.client.get("/chat")
        self.assertEqual(response.status_code, 200)
        title, = html.fromstring(response.data).cssselect("title")
        self.assertIn("chat channel", title.text.lower())

    def test_has_messages_table(self):
        """
        The chat view has a messages table. It has a table header with the
        appropriate headings, and a table body.
        """
        response = self.client.get("/chat")
        self.assertEqual(response.status_code, 200)
        table, = html.fromstring(response.data).cssselect("table.messages")
        time, name, message = table.cssselect("thead td")
        self.assertIn("time", time.text.lower())
        self.assertIn("name", name.text.lower())
        self.assertIn("thoughts", message.text.lower())

        tbody, = table.csselect("tbody")
        self.assertEqual(tbody.cssselect("tr"), [])
