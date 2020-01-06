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

Alternatively, add it using ``poetry``::

    poetry add django_localizer

Add it to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_localizer',
        ...
    )


To generate localizations, create a ``strings.stew`` file and then run

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

The new localization files are the ``*.stew`` files. You can have as many of
those as you wish, and you should keep them in your ``locale`` folders for your
applications. All the \*.stew files will be picked up and transformed into \*.po
files. Then those will be transformed into \*.mo files used by django.

Please, note that you should not modify the \*.po files manually as the changes
will be overwritten when you generate localizations the next time. That is
a common approach for all generated files.

For the file format, please, refer to the documentation of the ``stew`` library.

The two approaches to localization
++++++++++++++++++++++++++++++++++

Django takes a very distinct approach to localizing strings. With this approach,
you should write your text inside your ``trans`` tags or in your ``gettext``
function in such a way that it will be usable text even if there is no translation
for it:

.. code-block:: python

    prize = _('a car')
    print(_('You win %(prize)s') % {'prize': prize})

    # 'You win a car'

    # or, of course:
    print(_('You win'), _('a car'))

Things get even more complicated when you start dealing with plurals. By the
Django approach, this is what we should do:

The stew file::

    [%(n_foxes)s quick brown fox jumps over lazy dog #%(dog_number)s]
        en = A quick brown fox jumps over lazy dog #%(dog_number)s
        en[1] = %(n_foxes)s quick brown foxes jump over lazy dog #%(dog_number)s
        ru = Лиса перепрыгивает собаку №%(dog_number)s
        ru[1] = %(n_foxes)s лисы перепрыгивают собаку №%(dog_number)s
        ru[2] = %(n_foxes)s лис перепрыгивают собаку №%(dog_number)s
        ru[3] = %(n_foxes)s лис перепрыгивают собаку №%(dog_number)s

Which translates into the following bit in the Russian po file::

    msgid "%(n_foxes)s quick brown fox jumps over lazy dog #%(dog_number)s"
    msgid_plural "%(n_foxes)s quick brown fox jumps over lazy dog #%(dog_number)s"
    msgstr[0] "Лиса перепрыгивает собаку №%(dog_number)s"
    msgstr[1] "%(n_foxes)s лисы перепрыгивают собаку №%(dog_number)s"
    msgstr[2] "%(n_foxes)s лис перепрыгивают собаку №%(dog_number)s"
    msgstr[3] "%(n_foxes)s лис перепрыгивают собаку №%(dog_number)s"

If we want to process this in python code:

.. code-block:: python

    from django.utils import translation
    from django.utils.translation import ngettext

    translation.activate('ru')

    n = 4
    form = ngettext(
        '%(n_foxes)s quick brown fox jumps over lazy dog #%(dog_number)s',
        '%(n_foxes)s quick brown fox jumps over lazy dog #%(dog_number)s',
        n
    )
    f = form % {'n_foxes': n, 'dog_number': 5}
    print(f)

    # '4 лисы перепрыгивают собаку №5'

This feels like a lot of boilerplate code, but let's see what we should do in a
template::

    {% load i18n %}

    {% blocktrans count counter=n_foxes %}{{ n_foxes }} quick brown fox jumps over lazy dog #{{ dog_number }}{% plural %}{{ n_foxes }} quick brown fox jumps over lazy dog #{{ dog_number }}{% endblocktrans %}

And it is worth noting that you can't add linebreaks in this line because the
template engine will not be able to parse the tags or the formatting will change
the keys and the localization engine will not be able to find the strings in
the localization file.

There are certain advantages to this approach:

#. You will get human-readable text even if you don't have the translation,
   albeit in a different language;
#. You see the structure of the string and you know what variables it takes, so
   it is easier to populate it with actual data.

At the same time, there are disadvantages, too:

#. Because you always get *some* text, even if there are no translations for
   the string, it is more difficult to check that the string is actually
   translated;
#. Because the lookup key looks like normal text, when the string needs to be
   changed, very often the key will also change, which is a whole can of worms
   in itself;
#. Strings tend to change over time, and the number of placeholders may change,
   too. In this case, this approach requires changing the key as well.
#. The syntax is quite cumbersome, especially when it comes to plurals.

Keeping all that in mind, I tend to follow a different approach:

a. Treat your translation keys as just keys. Make them eloquent, but not actual
   text;
#. Add temporary translations to your \*.stew files as soon as you come up with
   a string;
#. As soon as the real translation is ready, add it to your stew file, don't
   modify the key ever again.

The stew file::

    [fox_jumps_dog]
        en = A quick brown fox jumps over lazy dog #{dog_number}
        en[1] = {} quick brown foxes jump over lazy dog #{dog_number}
        ru = Лиса перепрыгивает собаку №{dog_number}
        ru[1] = {} лисы перепрыгивают собаку №{dog_number}
        ru[2] = {} лис перепрыгивают собаку №{dog_number}
        ru[3] = {} лис перепрыгивают собаку №{dog_number}

The resulting .po file (Russian)::

    msgid "fox_jumps_dog"
    msgid_plural "fox_jumps_dog"
    msgstr[0] "Лиса перепрыгивает собаку №{dog_number}"
    msgstr[1] "{} лисы перепрыгивают собаку №{dog_number}"
    msgstr[2] "{} лис перепрыгивают собаку №{dog_number}"
    msgstr[3] "{} лис перепрыгивают собаку №{dog_number}"

To make this approach easier, I wrote a replacement for ``gettext`` and the
``trans`` tag, ``translate``:

.. code-block:: python

    from django_localizer import translate

    pk = 4
    print(translate('fox_jumps_dog', pk, dog_number=5))

    # '4 лисы перепрыгивают собаку №5'

Template code::

    {% load translate %}
    {% translate 'fox_jumps_dog' n_foxes dog_number=dog_number %}

The ``translate`` function
++++++++++++++++++++++++
Proper documentation will follow.

The signature is ``translate(key, *args, **kwargs)``

Key is the translation key that should be found in the translation files.

The next thing the function needs to know is whether the form should be plural
or singular. For that it must now the number. It looks for that number in the
following order:

1. The first ``*args`` argument if args are present;
#. The value of the first item in the ``**kwargs`` if kwargs has length 1
#. If kwargs are longer than 1, the value for the ``n`` key in kwargs if any

If the number could not be determined in that way, the key is deemed not to
have a plural form and will be looked for using ``gettext``. Otherwise ``ngettext``
will be used. However, if ``gettext`` returns a value which is identical to the
key, ``ngettext`` will be used to search further.

The string template found in this way will be populated with the parameters
passed in args and kwargs. The 'new-style' formatting is used (that is,
``str.format()``), thus you should use ``{}`` for placeholders in your string
templates.

This allows several approaches to placeholders in your strings:

1. Empty placeholder for the number of pluralized items::

    en[1] = {} quick brown foxes jump over lazy dog #{dog_number}

With this approach you can call the ``translate`` function with the number
of foxes in ``args``:

.. code-block:: python

    translate('fox_jumps_dog', 4, dog_number=3)

The ``4`` will be treated as the number of foxes.

If you want to use that number in several locations, you can use numbered
placeholders::

    en[1] = {0} quick brown foxes jump over lazy dog #{dog_number}. {0} is too many

2. Use the ``n`` parameter in the dictionary::

    en[1] = {n} quick brown foxes jump over lazy dog #{dog_number}. {n} is too many

.. code-block:: python

    translate('fox_jumps_dog', n=4, dog_number=3)

3. Use any key in the ``kwargs`` as long as it is the only key there::

    en[1] = {n_foxes} quick brown foxes jump over lazy dog.

.. code-block:: python

    translate('fox_jumps_dog', n_foxes=4)

The ``translate`` templatetag is a wrapper around this ``translate`` function and
has all the same properties.

Stew files
++++++++++

You can have as many stew files as you want. Naming does not matter as long as
the extension is ``.stew``. Django Localizer will look for them in the
``LOCALE_DIRS`` folder **and** in your apps' ``locale`` folders, in both cases
recursively. So you can have separate stew files for strings with different
intent, e.g. separate files for country names, error messages, push
notifications, etc. The strings from all those stew files will be merged into
the same ``.po`` files in the same locale dir (e.g. inside your application),
and special comments will be added with the path to the ``.stew`` files. The
sections from the ``.stew`` files are also preserved as comments::

    ### from my_app/locale/strings.stew

    # [[car]]
    msgid "A car"
    msgid_plural "{num} cars"
    msgstr[0] "Ein Auto"
    msgstr[1] "{num} Autos"


    ### from my_app/locale/counties.stew
    ...

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
