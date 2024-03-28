procyclingstats
===============

Procyclingstats is a Python package for scraping `procyclingstats.com`_,
which is a website with cycling stats. It's recommended to get familiar with
the website before using this package.

Installation
------------

Using pip:

.. code-block:: text

    $ pip install procyclingstats

Manual (for development):

.. code-block:: text

    $ git clone https://github.com/themm1/procyclingstats.git
    $ pip install -r procyclingstats/requirements_dev.txt

Basic usage
-----------

Basic Rider class usage:

.. code-block:: python

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
``RaceStartlist``, ``RaceClimbs``, ``Ranking``, ``Rider``, ``RiderResults``,
``Stage`` and ``Team``. Usage of all scraping classes is almost the same and
the only difference among them are parsing methods as is for example
``birthdate`` in Rider class usage example.

Unexpected behaviour and parsing errors
---------------------------------------

Since the project is a web scraper which parses HTML, it's difficult to make
it reliable and it's common to encounter some HTML parsing problems. After
getting some kind of unexpected behaviour or parsing errors, it's recommended
to update the package on your system using
``pip install procyclingstats --upgrade``. If the problem proceeds, see the
GitHub issues_ page and if the issue hasn't been opened yet, don't hesitate to
open one!

Links
-----

- GitHub_
- PyPI_
- Documentation_

.. _GitHub: https://github.com/themm1/procyclingstats
.. _PyPI: https://pypi.org/project/procyclingstats
.. _Documentation: https://procyclingstats.readthedocs.io/en/latest
.. _procyclingstats.com: https://www.procyclingstats.com
.. _selectolax: https://github.com/rushter/selectolax
.. _issues: https://github.com/themm1/procyclingstats/issues