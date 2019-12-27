=============================
django_localize
=============================

.. image:: https://badge.fury.io/py/django_localizer.svg
    :target: https://badge.fury.io/py/django_localizer

.. image:: https://travis-ci.org/therearesomewhocallmetim/django_localize.svg?branch=master
    :target: https://travis-ci.org/therearesomewhocallmetim/django_localize

.. image:: https://codecov.io/gh/therearesomewhocallmetim/django_localize/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/therearesomewhocallmetim/django_localize

A django module for turning strings.txt into po-mo files.

Documentation
-------------

The full documentation is at https://django_localize.readthedocs.io.

Quickstart
----------

Install django_localize::

    pip install django_localize

Looks like for now it is better to install it from github.

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_localize',
        ...
    )


To generate localizations, create `strings.txt` files and then run
.. code-block:: bash
    ./manage.py django-localize

It's best to keep your virtual environment outside of the project directory as
the command will process **all** .po files, including those in the virtialenv
directory.

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
