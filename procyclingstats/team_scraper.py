from typing import Any, Dict, List, Optional, Tuple

from .scraper import Scraper
from .select_parser import SelectParser
from .table_parser import TableParser
from .utils import get_day_month, join_tables, parse_table_fields_args, reg


class Team(Scraper):
    """
    Scraper for HTML team page.

    :param url: team URL, either absolute or relative, e.g.
    `team/bora-hansgrohe-2022`
    :param html: HTML to be parsed from, defaults to None, when passing the
    parameter, set `update_html` to False to prevent overriding or making
    useless request
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to make object ready for parsing, defaults to True
    """


    def __init__(self, url: str, html: Optional[str] = None,
                 update_html: bool = True) -> None:
        super().__init__(url, html, update_html)

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. Determines equality of objects (is
        used in __eq__ method).

        :return: Normalized URL in `team/{team_id}` format.
        """
        decomposed_url = self._decomposed_url()
        team_id = decomposed_url[1]
        return f"team/{team_id}"
   

    def _get_valid_url(self, url: str) -> str:
        """
        Validates given URL with regex and returns absolute URL

        :param url: URL either relative or absolute
        :raises ValueError: when URL isn't valid
        :return: absolute URL
        """
        team_url_regex = f"""
            {reg.base_url}?team{reg.team_url_str}
            ({reg.overview}{reg.anything}?)?\\/*
        """
        self._validate_url(url, team_url_regex,
                           "team/bora-hansgrohe-2022")
        return self._make_absolute_url(url)

    def teams_seasons_select(self, *args: str,
            available_fields: Tuple[str, ...] = (
                "text",
                "value"
            )) -> List[Dict[str, str]]:
        """
        Parses teams seasons select menu from HTML

        :return: table with fields `text`, `value` represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        team_seasons_select_html = self.html.css_first("form > select")
        s = SelectParser(team_seasons_select_html)
        s.parse(fields)
        return s.table

    def display_name(self) -> str:
        """
        Parses team display name from HTML

        :return: display name e.g. `BORA - hansgrohe`
        """
        display_name_html = self.html.css_first(".page-title > .main > h1")
        return display_name_html.text().split(" (")[0]

    def nationality(self) -> str:
        """
        Parses team's nationality from HTML

        :return: team's nationality as 2 chars long country code in uppercase
        """
        nationality_html = self.html.css_first(
            ".page-title > .main > span.flag")
        flag_class = nationality_html.attributes['class']
        return flag_class.split(" ")[1].upper() # type: ignore

    def team_status(self) -> str:
        """
        Parses team status from HTML

        :return: team status as 2 chars long code in uppercase e.g. `WT` (World
        Tour)
        """
        team_status_html = self.html.css_first(
            "div > ul.infolist > li:nth-child(1) > div:nth-child(2)")
        return team_status_html.text()

    def abbreviation(self) -> str:
        """
        Parses team abbreviation from HTML

        :return: team abbreviation as 3 chars long code in uppercase e.g. `BOH`
        (BORA - hansgrohe)
        """
        abbreviation_html = self.html.css_first(
            "div > ul.infolist > li:nth-child(2) > div:nth-child(2)")
        return abbreviation_html.text()

    def bike(self) -> str:
        """
        Parses team's bike brand from HTML

        :return: bike brand e.g. `Specialized`
        """
        bike_html = self.html.css_first(
            "div > ul.infolist > li:nth-child(3) > div:nth-child(2)")
        return bike_html.text()

    def wins_count(self) -> int:
        """
        Parses count of wins in corresponding season from HTML

        :return: count of wins in corresponding season
        """
        team_ranking_html = self.html.css_first(
            ".teamkpi > li:nth-child(1) > div:nth-child(2)")
        return int(team_ranking_html.text())

    def team_ranking_position(self) -> Optional[int]:
        """
        Parses team ranking position from HTML

        :return: PCS team ranking position in corresponding year
        """
        team_ranking_html = self.html.css_first(
            ".teamkpi > li:nth-child(2) > div:nth-child(2)")
        if team_ranking_html.text():
            return int(team_ranking_html.text())
        else:
            return None

    def riders(self, *args: str, available_fields: Tuple[str, ...] = (
            "nationality",
            "rider_name",
            "rider_url",
            "points",
            "age",
            "since",
            "until",
            "ranking_points",
            "ranking_position")) -> List[Dict[str, Any]]:
        """
        Parses team riders from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table with riders represented as list of dicts
        """
        casual_fields = [
            "nationality",
            "rider_name",
            "rider_url"]
        fields = parse_table_fields_args(args, available_fields)
        career_points_table_html = self.html.css_first("div.taba > ul.list")
        tp = TableParser(career_points_table_html)
        career_points_fields = [field for field in fields
                         if field in casual_fields]
        # add rider_url to the table for table joining purposes
        if "rider_url" not in career_points_fields:
            career_points_fields.append("rider_url")
        tp.parse(career_points_fields)
        if "career_points" in fields:
            career_points = tp.parse_extra_column(2,
                lambda x: int(x) if x.isnumeric() else 0)
            tp.extend_table("points", career_points)
        table = tp.table        

        # add ages to the table if needed
        if "age" in fields:
            ages_table_html = self.html.css_first("div.tabc > ul.list")
            ages_tp = TableParser(ages_table_html)
            ages_tp.parse(["rider_url"])
            ages = ages_tp.parse_extra_column(2)
            ages_tp.extend_table("age", ages)
            table = join_tables(table, ages_tp.table, "rider_url")

        # add ranking points and positions to the table if needed
        if "ranking_position" or "ranking_points" in fields:
            ranking_table_html = self.html.css_first("div.tabe > ul.list")
            ranking_tp = TableParser(ranking_table_html)
            ranking_tp.parse(["rider_url"])
            if "ranking_points" in fields:
                points = ranking_tp.parse_extra_column(2,
                    lambda x: x.replace("(", "").replace(")", ""))
                ranking_tp.extend_table("ranking_points", points)
            if "ranking_position" in fields:
                positions = ranking_tp.parse_extra_column(3,
                    lambda x: int(x) if x.isnumeric() else None)
                ranking_tp.extend_table("ranking_position", positions)
            table = join_tables(table, ranking_tp.table, "rider_url")

        # add rider's since and until dates to the table if needed
        if "since" in fields or "until" in fields:
            since_until_html_table = self.html.css_first("div.tabb > ul.list")
            since_tp = TableParser(since_until_html_table)
            since_tp.parse(["rider_url"])
            if "since" in fields:
                since_dates = since_tp.parse_extra_column(2,
                    lambda x: get_day_month(x) if "as from" in x else "01-01")
                since_tp.extend_table("since", since_dates)
            if "until" in fields:
                until_dates = since_tp.parse_extra_column(2,
                    lambda x: get_day_month(x) if "until" in x else "12-31")
                since_tp.extend_table("until", until_dates)
            table = join_tables(table, since_tp.table, "rider_url")

        # remove rider_url field if wasn't requested and was used for joining
        # tables only
        if "rider_url" not in fields:
            for row in table:
                row.pop("rider_url")
        return table
