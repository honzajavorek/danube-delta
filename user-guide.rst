How to use a blog based on Danube Delta?
========================================

For the sake of this user guide let's assume your blog is ``blog.python.cz``.

Installation
------------

Windows
~~~~~~~

Choose location on your disk where the blog is going to live. Let's say
``D:\blog.python.cz``. First, let's go to ``D:\``:

::

    C:\Users\kvetoslava> D:

Then let's clone blog's repository:

::

    $ git clone https://github.com/pyvec/blog.python.cz.git
    $ cd blog.python.cz

Then let's create a virtualenv folder and activate the virtualenv. Use Python 3,
please.

::

    D:\blog.python.cz> python -m venv venv
    D:\blog.python.cz> venv\Scripts\activate.bat

Now we need to install dependencies. Because Windows are the most
ridiculous OS on the planet, you can't just install whatever is in the
``requirements.txt`` file by ``pip``. You need to:

1.  Make sure you have the latest ``pip``. It's important.

    ::

        (venv) D:\blog.python.cz> python -m pip install pip --upgrade

2.  Manually download the ``lxml`` library in form of a *wheel* from
    `this unofficial
    registry <http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml>`__. Choose
    version appropriate for your Python and OS versions (e.g. ``cp35``
    means Python 3.5, ``win32`` means 32bit OS). Then install it inside
    your virtualenv:

    ::

        (venv) D:\blog.python.cz> pip install lxml-3.6.0-cp35-cp35m-win32.whl

3.  Now proceed with standard installation:

    ::

        (venv) D:\blog.python.cz> pip install -r requirements.txt

If everything went correctly, you should be ready at this point. You can
test everything works properly by running ``blog --help``:

::

    (venv) D:\blog.python.cz> blog --help

Linux / MacOS
~~~~~~~~~~~~~

Choose location on your disk where the blog is going to live. Let's say
``~/blog.python.cz``. Now let's clone blog's repository:

::

    $ git clone https://github.com/pyvec/blog.python.cz.git ~/blog.python.cz
    $ cd ~/blog.python.cz

Then let's create a virtualenv folder and activate the virtualenv. Use Python 3,
please.

::

    ~/blog.python.cz/$ python3 -m venv venv
    ~/blog.python.cz/$ . ./venv/bin/activate
    
* In some cases you may get an error:

:: 
    
    Error: Command '['/Users/your_name/blog.python.cz/venv/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1
    
Try solve it with command in ~/blog.python.cz/

::

    $ python3 -m venv venv --without-pip
    $ source venv/bin/activate
    

Now we need to install dependencies:

::

    (venv) ~/blog.python.cz/$ pip install -r requirements.txt

If everything went correctly, you should be ready at this point. You can
test everything works properly by running ``blog --help``:

::

    (venv) ~/blog.python.cz/$ blog --help

Writing Articles
----------------

1.  Before using the blog, you need to go to the directory where it lives
    and activate virtualenv. If ``blog --help`` doesn't work, then you're
    not ready yet.

2.  Before writing, make sure you download other people's changes from
    GitHub:

    ::

        blog update

3.  To start a new article, use:

    ::

        blog write

4.  To add photos to the article you just started, use:

    ::

        blog photos ../../my-photos/album/

    It should work also with a single picture:

    ::

        blog photos ../../my-photos/album/24340826629_d5bb5abb9e_o.jpg

5.  To locally verify how your changes are going to look like, use:

    ::

        blog preview

6.  When ready, publish your changes:

    ::

        blog publish

    When published, check `Travis
    CI <https://travis-ci.org/pyvec/blog.python.cz>`__ for possible
    errors. If it's green and there are no errors, the blog was
    successfully published and should be accessible from
    `blog.python.cz <http://blog.python.cz/>`__ in a minute or two.
