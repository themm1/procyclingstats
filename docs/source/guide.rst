
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
the URL (either relative or absolute). In order for the scraping class to work
correctly, the passed URL has to be in valid format (e.g.
``"rider/tadej-pogacar"`` for the :class:`Rider <procyclingstats.rider_scraper.Rider>`
class). There is an example of valid URL for each scraping class in it's
documentation. URL validating is no longer supported so it's only up to you to
decide whether valid HTML will be obtained from passed URL. If HTML from passed
URL isn't valid, the parsing methods won't work correctly.

To create an object ready for parsing without making request it's needed to
pass the HTML of the page as ``html`` parameter. URL has to be passed in that
case too. Passed HTML should be a string that is HTML from procyclingstats
page. You should also set the ``update_html`` parameter to ``False`` so request
to given URL isn't made. HTML that was passed or obtained from the page might
be also invalid in some cases. Invalid HTML looks usually like `this one`_.
When that is the case, ``ValueError`` is raised.

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
    :meth:`Race.prev_editions_select <procyclingstats.race_scraper.Race.prev_editions_select>`
    method for an example.

Some parsing methods might be unavailable with some HTMLs. In that case the
method raises ``ExpectedParsingError`` after being called. For an example, when
a :class:`Ranking <procyclingstats.ranking_scraper.Ranking>` scraping object is
created from a URL that points to a page with team ranking
:meth:`Ranking.individual_ranking <procyclingstats.stage_scraper.Stage.individual_ranking>`
method raises ``ExpectedParsingError``, because the ranking on the page isn't
an individual ranking. Use instead 
:meth:`Ranking.team_ranking <procyclingstats.stage_scraper.Stage.team_ranking>`
method to get the ranking.

Parsing all available data
--------------------------

When it's needed to get all parsable data from the page, use the 
:class:`parse <procyclingstats.scraper.Scraper.parse>` method. It calls all
the scraping methods of the scraping class and returns dictionary where keys
are called scraping methods and values are returned parsed values. See the
:class:`parse <procyclingstats.scraper.Scraper.parse>` method for more
information.

