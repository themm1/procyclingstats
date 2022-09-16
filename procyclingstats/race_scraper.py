from typing import Any, Dict, List

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import (format_regex_str, get_day_month, normalize_race_url,
                    parse_select, parse_table_fields_args, reg)


class Race(Scraper):
    """
    Scraper for race overview HTML page.

    Usage:

    >>> from procyclingstats import Race
    >>> race = Race("race/tour-de-france/2022/overview")
    >>> race.enddate()
    '2022-07-24'
    >>> race.parse()
    {
        'category': 'Men Elite',
        'edition': 109,
        'enddate': '2022-07-24',
        'is_one_day_race': False,
        ...
    }

    """
    _url_validation_regex = format_regex_str(
    f"""
        {reg.base_url}?race{reg.url_str}
        (({reg.year}{reg.stage}{reg.overview}{reg.anything}?)|
        ({reg.year}{reg.result}?{reg.overview}{reg.anything}?)|
        {reg.overview}{reg.anything}?)
        \\/*
    """)
    """Regex for validating race overview URL."""

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. Determines equality of objects (is
        used in __eq__ method).

        :return: Normalized URL in ``race/{race_id}/{year}/overview`` format.
            When year isn't contained in user defined URL, year is skipped.
        """
        return normalize_race_url(self._decompose_url(), "overview")

    def year(self) -> int:
        """
        Parse year when the race occured from HTML.

        :return: Year when the race occured.
        """
        return int(self.html.css_first("span.hideIfMobile").text())

    def name(self) -> str:
        """
        Parses display name from HTML.

        :return: Name of the race, e.g. ``Tour de France``.
        """
        display_name_html = self.html.css_first(".page-title > .main > h1")
        return display_name_html.text()

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is one day race from HTML.

        :return: Whether given race is one day race.
        """
        one_day_race_html = self.html.css_first("div.sub > span.blue")
        return "stage" not in one_day_race_html.text().lower()

    def nationality(self) -> str:
        """
        Parses race nationality from HTML.

        :return: 2 chars long country code in uppercase.
        """
        nationality_html = self.html.css_first(
            ".page-title > .main > span.flag")
        flag_class = nationality_html.attributes['class']
        return flag_class.split(" ")[1].upper() # type: ignore

    def edition(self) -> int:
        """
        Parses race edition year from HTML.

        :return: Edition as int.
        """
        edition_html = self.html.css_first(
            ".page-title > .main > span + font")
        if edition_html is not None:
            return int(edition_html.text()[:-2])
        raise ExpectedParsingError("Race cancelled, edition unavailable.")

    def startdate(self) -> str:
        """
        Parses race startdate from HTML.

        :return: Startdate in ``DD-MM-YYYY`` format.
        """
        startdate_html = self.html.css_first(
            ".infolist > li > div:nth-child(2)")
        return startdate_html.text()

    def enddate(self) -> str:
        """
        Parses race enddate from HTML.

        :return: Enddate in ``DD-MM-YYYY`` format.
        """
        enddate_html = self.html.css(".infolist > li > div:nth-child(2)")[1]
        return enddate_html.text()

    def category(self) -> str:
        """
        Parses race category from HTML.

        :return: Race category e.g. ``Men Elite``.
        """
        category_html = self.html.css(".infolist > li > div:nth-child(2)")[2]
        return category_html.text()

    def uci_tour(self) -> str:
        """
        Parses UCI Tour of the race from HTML.

        :return: UCI Tour of the race e.g. ``UCI Worldtour``.
        """
        uci_tour_html = self.html.css(".infolist > li > div:nth-child(2)")[3]
        return uci_tour_html.text()

    def prev_editions(self) -> List[Dict[str, str]]:
        """
        Parses previous race editions from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        editions_select_html = self.html.css_first("form > select")
        return parse_select(editions_select_html)

    def stages(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses race stages from HTML (available only on stage races). When
        race is one day race, empty list is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - date: Date when the stage occured in ``MM-DD`` format.
            - profile_icon: Profile icon of the stage (p1, p2, ... p5).
            - stage_name: Name of the stage, e.g \
                ``Stage 2 | Roskilde - Nyborg``.
            - stage_url: URL of the stage, e.g. \
                ``race/tour-de-france/2022/stage-2``.
            - distance: Stage distance in KMs as float.

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "date",
            "profile_icon",
            "stage_name",
            "stage_url",
            "distance"
        )
        if self.is_one_day_race():
            return []

        fields = parse_table_fields_args(args, available_fields)
        casual_fields = (
            "profile_icon",
            "stage_name",
            "stage_url"
        )
        stages_table_html = self.html.css_first("div:nth-child(3) > ul.list")
        # remove rest day table rows
        for stage_e in stages_table_html.css("li"):
            dist = stage_e.css_first("div:nth-child(5)").text()
            if not dist:
                stage_e.remove()

        table_parser = TableParser(stages_table_html)
        casual_f_to_parse = [f for f in fields if f in casual_fields]
        if casual_fields:
            table_parser.parse(casual_f_to_parse)
        # add stages dates to table if neede
        if "date" in fields:
            dates = table_parser.parse_extra_column(0, get_day_month)
            table_parser.extend_table("date", dates)
        # add distances to table if needed
        if "distance" in fields:
            distances = table_parser.parse_extra_column(4, lambda x:
                float(x.split("k")[0].replace("(", "")) if x else None)
            table_parser.extend_table("distance", distances)
        return table_parser.table
