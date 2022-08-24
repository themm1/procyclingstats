from typing import Any, Dict, List, Optional, Tuple

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import (format_regex_str, get_day_month, normalize_race_url,
                    parse_table_fields_args, reg)


class Race(Scraper):
    """
    Scraper for race overview page.

    :param url: URL of race overview either full or relative, e.g.
    `race/tour-de-france/2021/overview`
    :param html: HTML to be parsed from, defaults to None, when passing the
    parameter, set `update_html` to False to prevent overriding or making
    useless request
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to set HTML (when isn't passed), defaults to True
    """

    _url_validation_regex = format_regex_str(
    f"""
        {reg.base_url}?race{reg.url_str}
        (({reg.year}{reg.stage}{reg.overview}{reg.anything}?)|
        ({reg.year}{reg.result}?{reg.overview}{reg.anything}?)|
        {reg.overview}{reg.anything}?)
        \\/*
    """)
    """Regex for validating URL."""

    def __init__(self, url: str, html: Optional[str] = None,
                 update_html: bool = True) -> None:
        super().__init__(url, html, update_html)

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. Determines equality of objects (is
        used in __eq__ method).

        :return: Normalized URL in `race/{race_id}/{year}/overview` format.
        When year isn't contained in user defined URL, year is skipped.
        """
        return normalize_race_url(self._decomposed_url(), "overview")

    def year(self) -> int:
        """
        Parse year when the race occured

        :return: year
        """
        return int(self.html.css_first("span.hideIfMobile").text())

    def display_name(self) -> str:
        """
        Parses display name from HTML

        :return: display name e.g. `Tour de France`
        """
        display_name_html = self.html.css_first(".page-title > .main > h1")
        return display_name_html.text()

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is one day race from HTML

        :return: whether given race is one day race
        """
        one_day_race_html = self.html.css_first("div.sub > span.blue")
        return "stage" not in one_day_race_html.text().lower()

    def nationality(self) -> str:
        """
        Parses race nationality from HTML

        :return: 2 chars long country code
        """
        nationality_html = self.html.css_first(
            ".page-title > .main > span.flag")
        flag_class = nationality_html.attributes['class']
        return flag_class.split(" ")[1].upper() # type: ignore

    def edition(self) -> int:
        """
        Parses race edition year from HTML

        :return: edition as int
        """
        edition_html = self.html.css_first(
            ".page-title > .main > span + font")
        if edition_html is not None:
            return int(edition_html.text()[:-2])
        raise ExpectedParsingError("Race cancelled, edition unavailable.")

    def startdate(self) -> str:
        """
        Parses race startdate from HTML

        :return: startdate in `DD-MM-YYYY` format
        """
        startdate_html = self.html.css_first(
            ".infolist > li > div:nth-child(2)")
        return startdate_html.text()

    def enddate(self) -> str:
        """
        Parses race enddate from HTML

        :return: enddate in `DD-MM-YYYY` format
        """
        enddate_html = self.html.css(".infolist > li > div:nth-child(2)")[1]
        return enddate_html.text()

    def category(self) -> str:
        """
        Parses race category from HTML

        :return: race category e.g. `Men Elite`
        """
        category_html = self.html.css(".infolist > li > div:nth-child(2)")[2]
        return category_html.text()

    def uci_tour(self) -> str:
        """
        Parses UCI Tour of the race from HTML

        :return: UCI Tour of the race e.g. `UCI Worldtour`
        """
        uci_tour_html = self.html.css(".infolist > li > div:nth-child(2)")[3]
        return uci_tour_html.text()

    def stages(self, *args: str, available_fields: Tuple[str, ...] = (
            "date",
            "profile_icon",
            "stage_name",
            "stage_url",
            "distance")) -> List[Dict[str, Any]]:
        """
        Parses race stages from HTML (available only on stage races)

        :param *args: fields that should be contained in results table,
        available options are a all included in `fields` default value
        :param available_fields: default fields, all available options
        :raises Exception: when race is one day race
        :return: table with wanted fields represented as list of dicts
        """
        if self.is_one_day_race():
            raise ExpectedParsingError(
                "This method is available only on stage races")

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

        tp = TableParser(stages_table_html)
        casual_f_to_parse = [f for f in fields if f in casual_fields]
        if casual_fields:
            tp.parse(casual_f_to_parse)
        # add stages dates to table if neede
        if "date" in fields:
            dates = tp.parse_extra_column(0, lambda x: get_day_month(x))
            tp.extend_table("date", dates)        
        # add distances to table if needed
        if "distance" in fields:
            distances = tp.parse_extra_column(4, lambda x:
                float(x.split("k")[0].replace("(", "")) if x else None)
            tp.extend_table("distance", distances)
        return tp.table
