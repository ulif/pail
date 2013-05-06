pail -- Python Adaptive Images Library
=======================================

`pail` is a WSGI_ middleware providing `Adaptive Images`_. Delivering
small images to small devices.

It detects your visitor's screen size and automatically creates, and
delivers device appropriate re-scaled versions of your web page's
embeded HTML images. No (major) mark-up changes needed. It is intended
for use with `Responsive Designs`_ and to be combined with `Fluid
Image`_ techniques.

This package is based on the ideas of Matt Wilcox and (more loosely)
on his `PHP script`_ for the same purpose. Matt is in no way to blame for
any shortcomings of this Python port.

`pail` provides special support for use with Paste_.

Please note, that this package is still in a very early state and
changes, also to the API, are likely to happen in near future.

Comments and patches are welcome. Please send these to uli at gnufix
dot de.


Installation
------------

The package can be installed by::

  $ pip install pail

Afterwards you should be able to use pail in any WSGI_
environment. See the documentation_ for details.


Links
-----

- Full documentation_ (including deployment examples)
- `Fork me on GitHub`_

.. _documentation: http://packages.python.org/pail
.. _Adaptive Images: http://adaptive-images.com
.. _Responsive Designs: http://www.abookapart.com/products/responsive-web-design
.. _Fluid Image: http://unstoppablerobotninja.com/entry/fluid-images/
.. _Fork me on GitHub: http://github.com/ulif/pail
.. _WSGI: http://wsgi.readthedocs.org/en/latest/
.. _Paste: http://pythonpaste.org/
.. _PHP Script: http://github.com/mattwilcox/Adaptive-Images
