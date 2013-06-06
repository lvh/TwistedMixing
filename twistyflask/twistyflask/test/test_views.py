from axiom import store
from lxml import html
from twistyflask import app, log
from unittest import TestCase

class _ViewTestCaseMixin(object):
    """
    Common behavior for view tests.
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

    def get_tree(self, location):
        """
        Gets the page at location, then parses it.

        This explicitly uses a UTF-8 parser to work around a bug in
        lxml that prevents it from understanding HTML5 <meta> tag
        encoding specification.
        """
        response = self.client.get(location)
        parser = html.HTMLParser(encoding="utf-8")
        return html.fromstring(response.data, parser=parser)

    def test_well_behaved(self):
        """
        The page is well-behaved, and passes some basic sanity checks:
        right status code and encoding specification.

        The page explicitly specifies its encoding, UTF-8, in a meta tag,
        in the first 1024 bytes of the response. This relies on an exact
        spelling of that meta tag, as specified in a W3C recommendation.
        """
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertIn("""<meta charset="UTF-8">""", response.data[:1024])

class IndexTests(_ViewTestCaseMixin, TestCase):
    path = "/"

    def test_has_link_to_chat(self):
        """
        The index has a link to the chat page.
        """
        link, = self.getTree("/").cssselect("a[href$=chat]")
        self.assertIn("click here", link.text.lower())

class ChatTests(_ViewTestCaseMixin, TestCase):
    path = "/chat"

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
            timeCell, nameCell, messageCell = row.cssselect("td")

            timestamp = str(int(entry.time.asPOSIXTimestamp()))
            self.assertEqual(timeCell.text, timestamp)
            self.assertEqual(nameCell.text, entry.sender)
            self.assertEqual(messageCell.text, entry.message)

    def test_set_name_controls(self):
        """
        There is an input for entering your name.
        """
        self.assertTrue(self.getTree("/chat").cssselect("input#name"))

    def test_has_new_message_controls(self):
        """
        The chat view has an input bar for entering a new message, and a
        button for sending it. Both are disabled by default.
        """
        tree = self.getTree("/chat")
        for selector in ["input#new-message", "button#send-message"]:
            control, = tree.cssselect(selector)
            self.assertTrue(control.attrib.get("disabled"))

    def test_javascript(self):
        """
        The view loads jQuery, SockJS, and the chat logic, in order.
        """
        tree = self.getTree("/chat")
        jquery, sockjs, chatjs = tree.cssselect("body script")

        jqueryCDN = "http://code.jquery.com/jquery-1.10.1.min.js"
        self.assertEqual(jquery.attrib["src"], jqueryCDN)

        sockjsCDN = "http://cdn.sockjs.org/sockjs-0.3.min.js"
        self.assertEqual(sockjs.attrib["src"], sockjsCDN)

        self.assertEqual(chatjs.attrib["src"], "/static/chat.js")
