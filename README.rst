=============================
django_localize
=============================

.. image:: https://badge.fury.io/py/django_localize.svg
    :target: https://badge.fury.io/py/django_localize

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

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_localize.apps.DjangoLocalizeConfig',
        ...
    )

Add django_localize's URL patterns:

.. code-block:: python

    from django_localize import urls as django_localize_urls


    urlpatterns = [
        ...
        url(r'^', include(django_localize_urls)),
        ...
    ]

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
