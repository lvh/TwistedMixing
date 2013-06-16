=============
 twistyflask
=============

A silly demo combining Twisted and Flask.

Building, testing and running twistyflask
=========================================

This project uses tox to build and run virtualenvs within which to run
tests. If you would like to play around with it, it is recommended
that you install tox (using pip, for example), and then just run the
``tox`` command. This will create a virtualenv, install all
dependencies, and run all the tests.

Afterwards, you can activate a virtualenv like so::

    $ source .tox/py27/bin/activate

Then, you can start the daemon like so::

    $ twistd -n twistyflask

The ``-n`` flag prevents twistd from daemonizing, so you can see the
log events as they happen. The log should tell you which port is being
listened on. (By default, twistyflask tries to listen on port 0, which
will pick some random available port, depending on your OS.)

Point a browser to ``localhost:$PORT``, where ``$PORT`` is the
listening port you can see in the log.

Running twistyflask without tox
===============================

Run the following commands::

    $ pip install -r requirements.txt
    $ python setup.py install

Note that running twistyflask without using tox is not recommended.
