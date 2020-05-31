Installation
============

To install the latest version of `django_dicom`, simply run::

    pip install django_dicom

Once installed:

    * Add `django_dicom` to the `INSTALLED_APPS <https://docs.djangoproject.com/en/2.2/ref/settings/#installed-apps>`_ setting in your Django project's `settings.py <https://docs.djangoproject.com/en/2.2/topics/settings/>`_ file::

            INSTALLED_APPS = [
                ...
                'django_dicom',
            ]

    * `Include <https://docs.djangoproject.com/en/2.2/topics/http/urls/#url-namespaces-and-included-urlconfs>`_ `django_dicom`'s URLs in your project by adding the following line to the `urls.py <https://docs.djangoproject.com/en/2.2/topics/http/urls/>`_ file::

            urlpatterns = [
                ...
                path("api/", include("django_dicom.urls", namespace="dicom")),
            ]

    * Create the database tables::

            python manage.py makemigrations django_dicom
            python manage.py migrate django_dicom


    .. warning::
        `django_dicom` can only integrate with a `PostgreSQL <https://www.postgresql.org/>`_
        database. In order to set-up your project with `PostgreSQL <https://www.postgresql.org/>`_,
        try following this `DjangoGirls <https://tutorial-extensions.djangogirls.org/en/optional_postgresql_installation/>`_
        tutorial.

    * Start the development server and visit http://127.0.0.1:8000/admin/ or http://127.0.0.1:8000/dicom/.
