import calendar
from typing import List, Optional, Tuple

from .scraper import Scraper
from .table_parser import TableParser
from .utils import parse_table_fields_args, reg


class Rider(Scraper):
    """
    Scraper for HTML rider page.

    :param url: rider's URL either full or relative, e.g.
    `rider/tadej-pogacar`
    :param html: HTML to be parsed from, defaults to None, when passing the
    parameter, set `update_html` to False to prevent overriding or making
    useless request
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to set HTML (when isn't passed), defaults to True
    """

    def __init__(self, url: str, html: Optional[str] = None,
                 update_html: bool = True) -> None:
        super().__init__(url, html, update_html)

    def _get_valid_url(self, url: str) -> str:
        """
        Validates given URL with regex and returns absolute URL

        :param url: URL either relative or absolute
        :raises ValueError: when URL isn't valid
        :return: absolute URL
        """
        rider_url_regex = f"""
            {reg.base_url}?rider
            {reg.url_str}{reg.overview}?
            (\\/+)?
        """
        self._validate_url(url, rider_url_regex, "rider/tadej-pogacar")
        return self._make_absolute_url(url)

    def birthdate(self) -> str:
        """
        Parses rider's birthdate from HTML

        :return: birthday of the rider in `YYYY-MM-DD` format
        """
        general_info = self._html.find(".rdr-info-cont")[0].text.split("\n")
        birth_string = general_info[0].split(": ")[1]
        [date, month, year] = birth_string.split(" ")[:3]
        date = "".join([char for char in date if char.isnumeric()])
        month = list(calendar.month_name).index(month)
        return "-".join([str(year), str(month), date])

    def place_of_birth(self) -> str:
        """
        Parses rider's place of birth from HTML

        :return: rider's place of birth (town only)
        """
        # normal layout
        try:
            place_of_birth_html = self._html.find(
                ".rdr-info-cont > span > span > a")[0]
            return place_of_birth_html.text
        # special layout
        except IndexError:
            place_of_birth_html = self._html.find(
                ".rdr-info-cont > span > span > span > a")[0]
            return place_of_birth_html.text

    def name(self) -> str:
        """
        Parses rider's name from HTML

        :return: rider's name
        """
        return self._html.find(".page-title > .main > h1")[0].text

    def weight(self) -> int:
        """
        Parses rider's current weight from HTML

        :return: rider's weigth
        """
        # normal layout
        try:
            return int(self._html.find(".rdr-info-cont > span")
                       [1].text.split(" ")[1])
        # special layout
        except IndexError:
            return int(self._html.find(".rdr-info-cont > span > span")
                       [1].text.split(" ")[1])

    def height(self) -> float:
        """
        Parses rider's height from HTML

        :return: rider's height
        """
        # normal layout
        try:
            height_html = self._html.find(".rdr-info-cont > span > span")[0]
            return float(height_html.text.split(" ")[1])
        # special layout
        except IndexError:
            height_html = self._html.find(
                ".rdr-info-cont > span > span > span")[0]
            return float(height_html.text.split(" ")[1])

    def nationality(self) -> str:
        """
        Parses rider's nationality from HTML

        :return: rider's current nationality as 2 chars long country code in
        uppercase
        """
        # normal layout
        try:
            nationality_html = self._html.find(".rdr-info-cont > span")[0]
            return nationality_html.attrs['class'][1].upper()
        # special layout
        except KeyError:
            nationality_html = self._html.find(
                ".rdr-info-cont > span > span")[0]
            return nationality_html.attrs['class'][1].upper()

    def seasons_teams(self, *args: str, available_fields: Tuple[str, ...] = (
            "season",
            "since",
            "until",
            "team_name",
            "team_url",
            "class")) -> List[dict]:
        """
        Parses rider's teams per season from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        seasons_html_table = self._html.find("ul.list.rdr-teams")[0]
        tp = TableParser(seasons_html_table)
        casual_fields = [field for field in fields if field != "class"]
        tp.parse(casual_fields,
                 skip_when=lambda x: not x.find(".season")[0].text)
        # add class and convert it from `(WT)` to `WT`
        if "class" in fields:
            tp.extend_table("class", -3,
                            lambda x: x.replace("(", "").replace(")", ""))
        return tp.table

    def seasons_points(self, *args: str, available_fields: Tuple[str, ...] = (
            "season",
            "points",
            "position")) -> List[dict]:
        """
        Parses rider's points per season from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        points_table_html = self._html.find(".rdr-season-stats > tbody")[0]
        tp = TableParser(points_table_html)

        tp.parse(["season"])
        if "points" in fields:
            tp.extend_table("points", -2, int)
        if "position" in fields:
            tp.extend_table("position", -1, int)
        if "season" not in fields:
            for row in tp.table:
                row.pop("season")
        return tp.table
