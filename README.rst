=============================
django_localizer
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

Install django_localizer::

    pip install django_localizer

Alternatively, add it using `poetry`::

    poetry add django_localizer

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_localize',
        ...
    )


To generate localizations, create `strings.txt` files and then run

.. code-block:: bash

    ./manage.py generate_localizations

It's best to keep your virtual environment outside of the project directory as
the command will process **all** .po files, including those in the virtialenv
directory.

Features
--------

The main feature of this thing is the aggregation of all your translations into
a single text file. I find it significantly easier to keep all the translations
of one string in one place.

The new localization files are the `*.stew` files. You can have as many of
those as you wish, and you should keep them in your `locale` folders for your
applications. All the \*.stew files will be picked up and transformed into \*.po
files. Then those will be transformed into \*.mo files used by django.

Please, note that you should not modify the \*.po files manually as the changes
will be overwritten by when you generate localizations the next time. That is
a common approach for all generated files.

For the file format, please, refer to the documentation of the `stew` library.

The two approaches to localization
++++++++++++++++++++++++++++++++++

Django takes a very distinct approach to localizing strings. With this approach,
you should write your text inside your `trans` tags or in your `gettext`
function in such a way that it will be usable text even if there is no translation
for it::

    prize = _('a car')
    print(_('You win %(prize)s') % {'prize'=prize})

* TODO Check that the syntax is correct!

There are certain advantages to this approach:

1. You will get human-readable text even if you don't have the translation,
albeit in a different language

2. You see the structure of the string and you know what variables it takes, so
it is easier to populate it with actual data.

At the same time, there are certain disadvantages, too:

1. Because you always get _some_ text, even if there are no translations for
the string, it is more difficult to check that the string is actually
translated;

1. Because the lookup key looks like normal text, when the string needs to be
changed, very often the key will also change, which is a whole can of worms
in itself;

1. The syntax is quite cumbersome, especially when it comes to plurals.

Keeping all that in mind, I tend to follow a different approach:

a. Treat your translation keys as just keys. Make them eloquent, but not actual
text;

b. Add temporary translations to your \*.stew files as soon as you come up with
a string.

To make this approach easier, I wrote a replacement for gettext and the trans
tag, `translate`::

    from django_localizer import translate

    print(translate('my_key', x, a=3, b=4))

The `translate` function selects whether the string should be searched for using
`gettext` or `ngettext` and populates the retrieved string with the data.

The first thing the function needs to know is the number for the plural form.
It will check the first argument after `key`, if there isn't any,

More stuff here.

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
