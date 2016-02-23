Danube Delta
============

`Honza Javorek <https://github.com/honzajavorek/>`__'s `Pelican <http://www.getpelican.com/>`__ setup.

.. image:: https://travis-ci.org/honzajavorek/danube-delta.svg?branch=master
    :target: https://travis-ci.org/honzajavorek/danube-delta

Installation
------------

.. code:: shell

    $ pip install danube-delta

**Warning:** The library is only for Python 3.

Setup
-----

#.  Create scaffolding of your `Pelican <http://www.getpelican.com/>`__ blog:

    .. code:: shell

        $ mkdir ./my-awesome-blog
        $ cd ./my-awesome-blog
        $ git init
        $ mkdir ./content ./output
        $ echo '/output' > .gitignore

#.  Create ``./settings.py``:

    ..code:: python

        from danube_delta.settings import *

        AUTHOR = 'Zuzka & Honza'
        SITENAME = 'Pražení'

        if PRODUCTION:
            SITEURL = 'http://example.com'

#.  Install ``danube_delta``, globally:

    ..code:: shell

        $ sudo -H pip install danube_delta

#.  In the root of your blog directory you can now use the ``blog`` CLI:

    ..code:: shell

        $ blog write
        $ blog deploy

Usage
-----

..code:: shell

    $ blog write      # Starts a new article and opens it in your editor
    $ blog preview    # Opens preview of the blog in your browser
    $ blog publish    # Saves changes and sends them to GitHub

Developing Danube Delta
-----------------------

#.  Clone Danube Delta to a directory of your choice, e.g. ``~/danube-delta``.
#.  Install Danube Delta from your local clone: ``pip install -e ~/danube-delta``.

Name
----

I've seen some `pelicans <https://en.wikipedia.org/wiki/Pelican>`__ in the `Danube Delta <https://en.wikipedia.org/wiki/Danube_Delta>`__ in 2012:

.. figure:: danube-delta.jpg
   :alt: Pelicans in the Danube Delta

   Photo: © 2012 Honza Javorek
