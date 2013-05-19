.. _deployment:

Deployment -- How to Use `pail`
===============================

`pail` provides a `WSGI`_ middleware component compliant with
`Paste`_-based request and response objects.

.. code-block:: python

  from pail.wsgi import ImageAdaptingMiddleware

that does all the work. It requires a list of supported `resolutions`
(string with a comma-separated list of integers like ``"480, 922,
1322"``). Also a factory for this middleware is available:

.. code-block:: python

  from pail.wsgi import filter_app

that returns instances of the middleware. See the :ref:`api` for
details.

With `Paste`_
-------------

`pail` provides a `Paste`_-compatible `WSGI`_ filter app named
``main`` (this means that `Paste`_, once `pail` is installed, can find
the middleware as ``egg:pail`` automatically). It is meant to be used
as a `WSGI`_ application wrapper (a 'filter app' in `Paste`_ terms),
so that incoming requests are parsed, then passed to the wrapped
application and the result is scanned for image data before it is
passed on to the client.

A simple `Paste`_ config that makes use of `pail` might look like
this:

.. code-block:: ini

  [server:main]
  use = egg:Paste#http
  host = 0.0.0.0
  port = 8000

  [filter-app:main]
  use = egg:pail
  resolutions = 1024, 480
  next = static

  [app:static]
  use = egg:Paste#static
  document_root = %(here)s/static-dir/

Here the first section ``[server:main]`` defines a server listening on
port 8000.

The ``[app:static]`` section tells where the real content comes from:
it's simple static content read from local dir `static-dir`. We use
the `Paste`_ app `static` for that purpose.

The relevant part, however, is the second section
``[filter-app:main]``, where we tell `Paste`_ to filter the static
content through the `pail` filter app: ``use = egg:pail``.

Then we tell the `pail` filter to support the two resolutions of
`1024` and `480`: ``resolutions = 1024, 480``.

Finally we state to go on with the static app `static`: ``next =
static``. With `Paste`_ each filter app needs some other app (or filter
app) to filter.

Of course, this is only a very plain sample for a `WSGI`_/`Paste`_
setup. You could also create much more complex pipelines with several
other filters and adapting images from Plone, Diazo or other content
providers.

Also the content produced by `pail` could be mangled by further
filters in a `WSGI`_ pipeline; that's up to you. See the respective
`paste.deploy` documentation_ for details about `Paste`_ configuration
files.

Example
+++++++

Create a virtual environment, activate it, and install pail:

.. code-block:: console

   $ virtualenv py27   # also Python 2.6, 3.2, 3.3 should work
   $ source py27/bin/activate
   (py27)$ pip install pail

Create a `Paste`_ config in ``pailstatic.ini``:

.. code-block:: ini

  # pailstatic.ini
  #
  [server:main]
  # run an HTTP server on port 8000
  use = egg:Paste#http
  host = 0.0.0.0
  port = 8000

  [filter-app:main]
  # filter all requests through pail
  use = egg:pail
  resolutions = 1024, 480
  next = static

  [app:static]
  # serve static content...
  use = egg:Paste#static
  # ...from this local directory
  document_root = %(here)s/static/

Now create the static content:

.. code-block:: console

  (py27)$ mkdir static/
  (py27)$ cd static/

Create an HTML file named ``index.html`` like this:

.. code-block:: html

  <html>
    <head>
      <title>My test page</title>
      <script>
        document.cookie='resolution='+Math.max(
                        screen.width,screen.height)+'; path=/';
      </script>
    </head>
    <body>
      <div>Some Text</div>
      <img  style="width: 100%;" href="myimage.jpg" />
    </bod>
  </html>

and copy some image file, preferably a wide one (1024+ pixels width),
into the ``static/`` dir. Rename the image file to ``myimage.jpg``.

Now install the missing ``paster`` packages and start the server:

.. code-block:: console

  (py27)$ pip install PasteScript
  (py27)$ paster serve pailstatic.ini

Now, browsing http://localhost:8000/ you should see the generated page
with the image included. Nothing special. Nothing? If you are using a
desktop and the original image (put into the static dir) was wider
than 1024 pixels, while the desktop has a maximum resolution of
1024px, it should automatically have been *downscaled to 1024 px*
width. The same page watched from a mobile device with <= 480 px
screen width should automatically get an image with *width 480 px*.

You can force that switch on a single machine by replacing the
``Math.max()`` expression in the JavaScript part to some fixed value
like ``480``, ``960``, or whatever you want.

.. _Paste: http://pythonpaste.org/
.. _WSGI: http://wsgi.readthedocs.org/en/latest/
.. _documentation: http://pythonpaste.org/deploy/
