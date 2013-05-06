.. _how_it_works:

How it works
============

`pail` does a number of things depending on the scenario, the
component has to handle but here's a basic overview of what happens
when you load a page with `pail` enabled on the server:

#) The HTML starts to load in the browser and a snippet of JS in the
   ``<head>`` writes a cookie, storing the visitor's screen size in
   pixels.

#) The browser then encounters an ``<img>`` tag and sends a request to
   the server for that image. It also sends the cookie, because that's
   how browsers work.

#) The web server sends the incoming request to the local WSGI app with
   `pail` acting as a filter somewhere in the pipeline of WSGI apps.

#) `pail` feeds any wrapped WSGI_ application (the real content
   provider) and receives some HTTP response from that application
   which also includes the image requested by the visitor.

#) `pail` looks for a cookie and finds, that the user has a maximum
   screen size of 480px.

#) It compares the cookie value with all ``resolutions`` that were
   configured, and decides which matches best. In this case, an image
   maxing out at 480px wide.

#) It checks the image width. If that's smaller than the user's screen
   width it sends the image unchanged.

#) If it is larger, `pail` creates a down-scaled copy and sends it to
   the user.

`pail` also does a few other things when needs arise, for example:

- Detects Retina displays. You can choose to serve high DPI images to
  those displays if you want, by using an alternate line of
  JavaScript.

- It handles cases where there isn't a cookie set; mobile devices will
  be supplied the smallest image, and desktop devices will get the
  largest.

There are also some things, `pail` does **not** support currently (and
which the original PHP script does):

- There is no caching yet.

- Cache headers are not set correctly yet.

.. _WSGI: http://wsgi.readthedocs.org/en/latest/
