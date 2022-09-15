
.. _this one: https://www.procyclingstats.com/race/tdf

Guide
=====

This is an usage guide for the procyclingstats package. For more detailed
information about the concrete scraping classes and methods see the
:ref:`API <api>` page.

Creating scraping objects
-------------------------

All scraping classes have the 
:meth:`Scraper constructor <procyclingstats.scraper.Scraper.__init__>`. The 
easiest way to create scraping object that is ready for parsing is by passing
the URL (either relative or absolute). When the URL is valid for the scraping
class (e.g. URLs in ``"rider/{rider_id}"`` format are valid for the
:class:`Rider <procyclingstats.rider_scraper.Rider>` class), the object is
created successfully. Otherwise ``ValueError`` is raised. Passed URL doesn't
have to be only in this format, because every scraping class has it's own regex
for validating URLs. So for the
:class:`Rider <procyclingstats.rider_scraper.Rider>` class valid URLs are also
``"rider/{rider_id}/"`` or ``"rider/{rider_id}/overview"``. Basically every URL
that points to page with parsable HTML should be valid.
For some classes (:class:`Ranking <procyclingstats.ranking_scraper.Ranking>`, 
:class:`RiderResults <procyclingstats.rider_results_scraper.RiderResults>`) are
valid also filter URLs. E.g. for
:class:`Ranking <procyclingstats.ranking_scraper.Ranking>` class is
``"rankings.php?date=2021-12-31&p=me&s=season-individual"`` a valid URL. 

To create an object ready for parsing without making request it's needed to
pass the HTML of the page as ``html`` parameter. URL has to be passed in that
case too. Passed HTML should be a string that is HTML from procyclingstats
page. You should also set the ``update_html`` parameter to ``False`` so request
to given URL isn't made. HTML that was passed or obtained from the page might
be also invalid in some cases. Invalid HTML looks usually like `this one`_.
When that is the case ``ValueError`` is raised.

Parsing methods
---------------

When scraping object is ready for parsing, use parsing methods to get data
from the HTML. Parsing methods differs among scraping classes and all of them
are documented on the :ref:`API <api>` page. There are three types of parsing
methods:

- Basic parsing methods
    Parses only one piece of information from the HTML. See
    :meth:`Rider.birthdate <procyclingstats.rider_scraper.Rider.birthdate>`
    method for an example.

- Table parsing methods
    Parses table or unordered list from the HTML and returns it as list of
    dicts where dict keys are wanted fields which are passed as arguments. See 
    :meth:`Rider.teams_history <procyclingstats.rider_scraper.Rider.teams_history>`
    method for an example.

- Select menu parsing methods
    Parses select menu from HTML and returns it as list of dicts where dict
    keys are always ``"text"`` and ``"value"``. See 
    :meth:`Race.prev_editions <procyclingstats.race_scraper.Race.prev_editions>`
    method for an example.

Some parsing methods might be unavailable with some HTMLs. In that case the
method raises ``ExpectedParsingError`` after being called. For an example, when
a :class:`Stage <procyclingstats.stage_scraper.Stage>` scraping object is
created from a page with one day race, the
:meth:`Stage.gc <procyclingstats.stage_scraper.Stage.gc>` method raises
``ExpectedParsingError`` because one day races don't have general
classification.

Parsing all available data
--------------------------

When it's needed to get all parsable data from the page, use the 
:class:`parse <procyclingstats.scraper.Scraper.parse>` method. It calls all
the scraping methods of the scraping class and returns dictionary where keys
are called scraping methods and values are returned parsed values. See the
:class:`parse <procyclingstats.scraper.Scraper.parse>` method for more
information.

Comparing scraping objects
--------------------------

Objects are equal when URLs returned by
:class:`normalized_relative_url <procyclingstats.scraper.Scraper.normalized_relative_url>`
are the same. When objects are equal, it means that the
:class:`parse <procyclingstats.scraper.Scraper.parse>` method of both objects
should return the same dictionary. However when objects aren't equal, dicts
returned by their :class:`parse <procyclingstats.scraper.Scraper.parse>`
methods may also be the same in some cases. For example 
``Race("race/tour-de-france") != Race("race/tour-de-france/2022")`` is `True`
even if in 2022 URLs of both objects point to the same page. The equality is
determined solely from URL, so HTML isn't needed for comparing objects.
