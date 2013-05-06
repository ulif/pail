.. _developers:

Developers' Instructions
------------------------

These are instructions for developers that want to develop `pail`
itself - not for users or webmasters.

Before starting any further work it is highly recommended to create
and activate a virtualenv:

.. code-block:: console

  $ virtualenv py27
  $ source py27/bin/activate
  (py27)$

Here we used a Python 2.7 install but `pail` is also tested with
Python 2.6, 3.2, and 3.3.

Now get the source via GitHub_

.. _GitHub: http://github.com/ulif/pail

.. code-block:: console

  $ git clone https://github.com/ulif/pail

and change into the created `pail/` directory.

The development setup is done with:

.. code-block:: console

  (py27)$ python setup.py dev

This step mainly installs the required external packages (mainly
`Pillow` and `WebOb`) and needed testing components (`py.test` and
`pytest-cov`) locally in your virtualenv.

Testing
+++++++

`pail` testing uses `py.test`. The recommended way to run tests is
therefore:

.. code-block:: console

  (py27)$ py.test

`py.test` should be installed already if you completed the steps
above.

You could also run ``$ python setup.py tests``, but this approach is
less flexible. For instance you currently cannot pass arguments to the
test-runner.

For testing with several Python versions in one row `pail` also
provides a ``tox.ini``. So, if you have tox_ installed, you can run
tests for different Python versions like this:

.. code-block:: console

  (py27)$ pip install tox  # required only once
  (py27)$ tox

Modify `tox.ini` to your needs.

Test-Coverage
+++++++++++++

A coverage report can also be created with:

.. code-block:: console

  (py27)$ py.test --cov=pail --cov-report=html

Results can be found in `htmlcov/` afterwards. Before submitting
patches please make sure that test coverage is at 100%.

Spinx-Docs
++++++++++

The `pail` docs are created using `Sphinx`_. The required packages can
be installed locally doing:

.. code-block:: console

  (py27)$ python setup.py docs

This will not generate the docs but install the packages needed to
create the docs, most notably `Sphinx`_.

The actual docs can then be created with:

.. code-block:: console

  (py27)$ sphinx-build docs/ docs/_build/html

Sources for the docs can be found (you guessed it) in the ``docs/``
directory.

.. _tox: https://pypi.python.org/pypi/tox
.. _Sphinx: http://sphinx-doc.org/
