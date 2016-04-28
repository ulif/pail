# from distutils.core import setup, Command
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

tests_path = os.path.join(os.path.dirname(__file__), 'tests')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        args = sys.argv[sys.argv.index('test')+1:]
        self.test_args = args
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

install_requires = [
    'setuptools',
    'Pillow',
    'webob',
    ]

tests_require = [
    'pytest',
    'pytest-cov',
    'Pillow',
    ]

docs_require = ['Sphinx', 'Pygments']

setup(
    name='pail',
    version='0.3.dev0',
    author='Uli Fouquet',
    author_email='uli@gnufix.de',
    packages=['pail', 'pail.tests'],
    scripts=[],
    url='http://pypi.python.org/pypi/pail/',
    license='LICENSE.txt',
    description='Pyton Adaptive Imaging Library.',
    long_description=open('README.rst').read() + '\n\n' + open(
        'CHANGES.txt').read() + '\n\n' + 'Download\n********\n',
    classifiers=['Development Status :: 3 - Alpha',
                 'Framework :: Buildout',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 ],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require = dict(
        tests = tests_require,
        docs = docs_require,
        ),
    cmdclass = {'test': PyTest},
    zip_safe = False,
    entry_points="""[paste.filter_app_factory]
    main = pail.wsgi:filter_app
    """,
)
