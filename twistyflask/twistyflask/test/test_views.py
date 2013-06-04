from axiom import store
from lxml import html
from twistyflask import app, log
from unittest import TestCase


class _ViewTestCaseMixin(object):
    """
    Common set up and tear down behavior for view tests.
    """
    def setUp(self):
        """
        Creates a test client, and puts the app in testing and debug mode.
        """
        app.store = store.Store()
        self.client = app.test_client()
        app.testing = True
        app.debug = True

    def tearDown(self):
        """
        Turns the app's debug and testing modes off.
        """
        app.testing = False
        app.debug = False

    def getTree(self, location):
        """
        Gets the page at location, then parses it.

        This explicitly uses a UTF-8 parser to work around a bug in
        lxml that prevents it from understanding HTML5 <meta> tag
        encoding specification.
        """
        response = self.client.get(location)
        parser = html.HTMLParser(encoding="utf-8")
        return html.fromstring(response.data, parser=parser)

    def assertSpecifiesEncoding(self, response):
        """
        The page explicitly specifies its encoding, UTF-8, in a meta tag,
        in the first 1024 bytes of the response. This relies on an exact
        spelling of that meta tag, as specified in a W3C recommendation.
        """
        tag = """<meta charset="UTF-8">"""
        self.assertIn(tag, response.data[:1024])

class IndexTests(_ViewTestCaseMixin, TestCase):
    def test_well_behaved(self):
        """
        The index returns with a 200 response and specifies its encoding.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertSpecifiesEncoding(response)

    def test_has_link_to_chat(self):
        """
        The index has a link to the chat page.
        """
        link, = self.getTree("/").cssselect("a[href$=chat]")
        self.assertIn("click here", link.text.lower())

class ChatTests(_ViewTestCaseMixin, TestCase):
    def test_well_behaved(self):
        """
        The chat page returns with a 200 response and specifies its encoding.
        """
        response = self.client.get("/chat")
        self.assertEqual(response.status_code, 200)
        self.assertSpecifiesEncoding(response)

    def test_chat_in_title(self):
        """
        The chat view advertises itself in its title.
        """
        title, = self.getTree("/chat").cssselect("title")
        self.assertIn("chat channel", title.text.lower())

    def test_has_messages_table(self):
        """
        The chat view has a messages table. It has a table header with the
        appropriate headings, and a table body. The table body contains the
        messages in the log.
        """
        def makeEntry(sender, message):
            entry = log.LogEntry(
                store=app.store, sender=sender, message=message)
            return entry

        entries = [
            makeEntry(u"\N{SNOWMAN}", u"\N{RADIOACTIVE SIGN}"),
            makeEntry(u"\N{FEMALE SIGN}", u"\N{BLACK SUN WITH RAYS}"),
            makeEntry(u"\N{SNOWMAN}", u"\N{BIOHAZARD SIGN}")
        ]

        table, = self.getTree("/chat").cssselect("table.messages")
        time, name, message = table.cssselect("thead td")
        self.assertIn("time", time.text.lower())
        self.assertIn("name", name.text.lower())
        self.assertIn("thoughts", message.text.lower())

        rows = table.cssselect("tbody tr")
        self.assertEqual(len(rows), len(entries))

        for row, entry in zip(rows, entries):
            _time, nameCell, messageCell = row.cssselect("td")
            self.assertEqual(entry.sender, nameCell.text)
            self.assertEqual(entry.message, messageCell.text)
