import calendar
from typing import Any, Dict, List, Tuple

from selectolax.parser import HTMLParser

from .scraper import Scraper
from .table_parser import TableParser
from .utils import (format_regex_str, get_day_month, parse_table_fields_args,
                    reg)


class Rider(Scraper):
    """Scraper for rider HTML page. Example URL: `rider/tadej-pogacar`."""
    _url_validation_regex = format_regex_str(
    f"""
        {reg.base_url}?rider
        {reg.url_str}({reg.overview}{reg.anything}?|
        {reg.year}{reg.anything}?)?
        \\/*
    """)
    """Regex for validating rider URL."""

    @staticmethod
    def _html_invalid(html: HTMLParser) -> bool:
        """
        Overrides `Scraper` method. HTML is considered invalid when page title
        is 'Start'.

        :param html: HTML to validate
        :return: True if given HTML is invalid, otherwise False
        """
        page_title = html.css_first(".page-title > .main > h1").text()
        return page_title == "Start"

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. Determines equality of objects (is
        used in __eq__ method).

        :return: Normalized URL in `rider/{rider_id}` format.
        """
        decomposed_url = self._decompose_url()
        rider_id = decomposed_url[1]
        return f"rider/{rider_id}"

    def birthdate(self) -> str:
        """
        Parses rider's birthdate from HTML

        :return: birthday of the rider in `YYYY-MM-DD` format
        """
        general_info_html = self.html.css_first(".rdr-info-cont")
        bd_string = general_info_html.text(separator=" ", deep=False)
        bd_list = [item for item in bd_string.split(" ") if item][:3]
        [day, str_month, year] = bd_list
        month = list(calendar.month_name).index(str_month)
        return f"{year}-{month}-{day}"

    def place_of_birth(self) -> str:
        """
        Parses rider's place of birth from HTML

        :return: rider's place of birth (town only)
        """
        # normal layout
        try:
            place_of_birth_html = self.html.css_first(
                ".rdr-info-cont > span > span > a")
            return place_of_birth_html.text()
        # special layout
        except AttributeError:
            place_of_birth_html = self.html.css_first(
                ".rdr-info-cont > span > span > span > a")
            return place_of_birth_html.text()

    def name(self) -> str:
        """
        Parses rider's name from HTML

        :return: rider's name
        """
        return self.html.css_first(".page-title > .main > h1").text()

    def weight(self) -> int:
        """
        Parses rider's current weight from HTML

        :return: rider's weigth
        """
        # normal layout
        try:
            weight_html = self.html.css(".rdr-info-cont > span")[1]
            return int(weight_html.text().split(" ")[1])
        # special layout
        except (AttributeError, IndexError):
            weight_html = self.html.css(".rdr-info-cont > span > span")[1]
            return int(weight_html.text().split(" ")[1])

    def height(self) -> float:
        """
        Parses rider's height from HTML

        :return: rider's height
        """
        # normal layout
        try:
            height_html = self.html.css_first(".rdr-info-cont > span > span")
            return float(height_html.text().split(" ")[1])
        # special layout
        except (AttributeError, IndexError):
            height_html = self.html.css_first(
                ".rdr-info-cont > span > span > span")
            return float(height_html.text().split(" ")[1])

    def nationality(self) -> str:
        """
        Parses rider's nationality from HTML

        :return: rider's current nationality as 2 chars long country code in
        uppercase
        """
        # normal layout
        nationality_html = self.html.css_first(".rdr-info-cont > .flag")
        if nationality_html is None:
        # special layout
            nationality_html = self.html.css_first(
                ".rdr-info-cont > span > span")
        flag_class = nationality_html.attributes['class']
        return flag_class.split(" ")[-1].upper() # type:ignore


    def seasons_teams(self, *args: str, available_fields: Tuple[str, ...] = (
            "season",
            "since",
            "until",
            "team_name",
            "team_url",
            "class")) -> List[Dict[str, Any]]:
        """
        Parses rider's teams per season from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        seasons_html_table = self.html.css_first("ul.list.rdr-teams")
        tp = TableParser(seasons_html_table)
        casual_fields = [f for f in fields
                         if f in ("season", "team_name", "team_url")]
        if casual_fields:
            tp.parse(casual_fields)
        if "class" in fields:
            classes = tp.parse_extra_column(2,
                lambda x: x.replace("(", "").replace(")", "").replace(" ", "")
                if x and "retired" not in x else None)
            tp.extend_table("class", classes)
        if "since" in fields:
            until_dates = tp.parse_extra_column(-2,
                lambda x: get_day_month(x) if "as from" in x else "01-01")
            tp.extend_table("since", until_dates)
        if "until" in fields:
            until_dates = tp.parse_extra_column(-2,
                lambda x: get_day_month(x) if "until" in x else "12-31")
            tp.extend_table("until", until_dates)

        table = [row for row in tp.table if row['class']]
        return table

    def seasons_points(self, *args: str, available_fields: Tuple[str, ...] = (
            "season",
            "points",
            "rank")) -> List[Dict[str, Any]]:
        """
        Parses rider's points per season from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        points_table_html = self.html.css_first("table.rdr-season-stats")
        tp = TableParser(points_table_html)
        tp.parse(fields)
        return tp.table
