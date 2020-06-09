Installation
============

To install the latest version of *django_dicom*, simply run::

    pip install django_dicom

Once installed:

    * Add *django_dicom* to the INSTALLED_APPS_:

      .. code-block:: python
        :caption: settings.py

        INSTALLED_APPS = [
            ...
            'django_dicom',
        ]

    * Include *django_dicom*\'s URLs:

    .. code-block:: python
        :caption: urls.py

        urlpatterns = [
            ...
            path("api/", include("django_dicom.urls", namespace="dicom")),
        ]

    * Create the database tables::

            python manage.py migrate django_dicom


    .. warning::
        `django_dicom` can only integrate with a PostgreSQL_ database. In order
        to set-up your project with PostgreSQL follow `this DjangoGirls
        tutorial`_.

    * Start the development server and visit http://127.0.0.1:8000/admin/ or
    http://127.0.0.1:8000/dicom/.

.. _INSTALLED_APPS:
   https://docs.djangoproject.com/en/3.0/ref/settings/#installed-apps
.. _PostgreSQL: https://www.postgresql.org
.. _this DjangoGirls tutorial:
   https://tutorial-extensions.djangogirls.org/en/optional_postgresql_installation