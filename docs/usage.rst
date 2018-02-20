=====
Usage
=====

To use django_localize in a project, add it to your `INSTALLED_APPS`:

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
