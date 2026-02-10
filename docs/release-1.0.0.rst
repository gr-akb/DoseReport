###################################
OpenREM Release Notes version 1.0.0
###################################

****************
Headline changes
****************

* Python 3
* Django 2.2
* Docker or direct install on Windows and Linux
* Celery, Flower and RabbitMQ removed from requirements

* Performing physician added to standard fluoroscopy exports (:issue:`840`)
* Station name checked at series level only, option to check at study level only instead (:issue:`772`)

Upgrade from 1.0.0b1 or 1.0.0b2
===============================

Docker
------

Linux
-----

Recommended Python version has been updated to 3.12; 3.10 and 3.11 should be ok still but you might want to upgrade.

Activate the virtualenv (note the ``.`` -- you can also use the word ``source``):

.. code-block:: console

    $ . /var/dose/veopenrem3/bin/activate

.. code-block:: console

    $ pip install openrem==1.0.0b3

.. code-block:: console

    $ python manage.py makemigrations remapp
    $ python manage.py migrate
    $ python manage.py loaddata openskin_safelist.json
    $ python manage.py collectstatic --no-input --clear
    $ python manage.py compilemessages

Restart the services:

.. code-block:: console

    $ sudo systemctl restart openrem-gunicorn.service
    $ sudo systemctl restart redis-server.service
    $ sudo systemctl restart openrem-consumer.service

Windows
-------

Recommended Python version has been updated to 3.12; 3.10 and 3.11 should be ok still but you might want to upgrade.

In a ``CMD`` window, move to the openrem Python folder and activate the virtualenv:

.. code-block:: console

    C:\Users\openrem>e:
    E:\>cd venv\Lib\site-packages\openrem
    E:\venv\Lib\site-packages\openrem>e:\venv\Scripts\activate
    (venv) E:\venv\Lib\site-packages\openrem>

.. code-block:: console

    (venv) E:\>pip install openrem==1.0.0b3

.. code-block:: console

    (venv) E:\venv\Lib\site-packages\openrem>python manage.py makemigrations remapp
    (venv) E:\venv\Lib\site-packages\openrem>python manage.py migrate
    (venv) E:\venv\Lib\site-packages\openrem>python manage.py loaddata openskin_safelist.json
    (venv) E:\venv\Lib\site-packages\openrem>python manage.py collectstatic --no-input --clear

*Restart the services...*

Upgrade from 0.10.0
===================

Review the :doc:`installation` doc to find the upgrade options

Upgrade from an older version
=============================

:doc:`upgrade_previous_0.10.0`
