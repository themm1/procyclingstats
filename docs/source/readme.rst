About
-----

Procyclingstats is a python package for scraping procyclingstats.com_, which is
a website with cycling stats. It uses Cython selectolax_ libarary for HTML
parsing which is blazingly fast.

Instalation
-----------

Using pip (NOT AVAILABLE YET):

.. code-block:: text

    pip install procyclingstats

Manual (for development):

.. code-block:: text

    git clone https://github.com/themm1/procyclingstats.git
    pip install -r requirements_dev.txt

Basic usage
-----------

Basic Rider class usage:

>>> from procyclingstats import Rider
>>> rider = Rider("rider/tadej-pogacar")
>>> rider.birthdate()
"1998-9-21"
>>> rider.parse()
{
    'birthdate': '1998-9-21',
    'height': 1.76,
    'name': 'Tadej  Pogačar',
    'nationality': 'SI',
    ...
}

Interface consists from scraping classes which are currently ``Race``,
``RaceStartlist``, ``Ranking``, ``Rider``, ``RiderResults``, ``Stage`` and
``Team``. Usage of all scraping classes is almost the same and the only
difference among them are parsing methods as is for example ``birthdate`` in
Rider class usage example.

.. _procyclingstats.com: https://www.procyclingstats.com
.. _selectolax: https://github.com/rushter/selectolax

