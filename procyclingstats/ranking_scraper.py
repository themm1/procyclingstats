from typing import Any, Dict, List, Literal, Optional, Tuple

from selectolax.parser import Node

from .errors import ExpectedParsingError
from .scraper import Scraper
from .select_parser import SelectParser
from .table_parser import TableParser
from .utils import format_url_filter, parse_table_fields_args, reg


class Ranking(Scraper):
    """
    Scraper for HTML ranking page. Always only one method for ranking
    parsing is available (based on ranking type). e.g. `self.individual_ranking`
    for `rankings/me/season-individual` ranking

    :param url: URL of ranking to be parsed from, either full or relative,
    e.g. `rankings/me/season-individual` or URL with filters
    :param html: HTML to be parsed from, defaults to None, when passing the
    parameter, set `update_html` to False to prevent overriding or making
    useless request
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to set HTML (when isn't passed), defaults to True
    """
    _url_validation_regex = f"{reg.base_url}?rankings.*\\/*"
    """Regex for validating ranking URL."""

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. Determines equality of objects (is
        used in __eq__ method). Ranking objects are equal when both have same
        URL or filter values are the same (empty filter values don't count).

        :return: formatted relative URL or filter URL without uneccessary fields
        e.g. `rankings.php?date=2021-12-31&p=we&s=season-individual`
        """
        relative_url = self.relative_url()
        # returns special normalized ranking filter URL
        if "?" in relative_url:
            return format_url_filter(relative_url)
        decomposed_url = self._decomposed_url()
        # remove .php from rankings URL if it is not a filter URL
        if "." in decomposed_url[0]:
            decomposed_url[0] = decomposed_url[0].split(".")[0]
        return "/".join(decomposed_url)

    def individual_ranking(self, *args: str,
                           available_fields: Tuple[str, ...] = (
                               "rank",
                               "prev_rank",
                               "rider_name",
                               "rider_url",
                               "team_name",
                               "team_url",
                               "nationality",
                               "points")) -> List[Dict[str, Any]]:
        """
        Parses individual ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have individual ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "individual":
            raise ExpectedParsingError(
                "This object doesn't support individual_ranking method, create"
                "one with individual ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def team_ranking(self, *args: str, available_fields: Tuple[str, ...] = (
            "rank",
            "prev_rank",
            "team_name",
            "team_url",
            "nationality",
            "class",
            "points")) -> List[Dict[str, Any]]:
        """
        Parses team ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have teams ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "teams":
            raise ExpectedParsingError(
                "This object doesn't support team_ranking method, "
                "create one with teams ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def nations_ranking(self, *args: str, available_fields: Tuple[str, ...] = (
            "rank",
            "prev_rank",
            "nation_name",
            "nation_url",
            "nationality",
            "points")) -> List[Dict[str, Any]]:
        """
        Parses nations ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have nations ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "nations":
            raise ExpectedParsingError(
                "This object doesn't support nations_ranking method, create one"
                "with nations ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def races_ranking(self, *args: str, available_fields: Tuple[str, ...] = (
            "rank",
            "prev_rank",
            "race_name",
            "race_url",
            "nationality",
            "class",
            "points")) -> List[Dict[str, Any]]:
        """
        Parses races ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have races ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "races":
            raise ExpectedParsingError(
                "This object doesn't support races_ranking method, create one"
                "with race ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.css_first("table")
        tp = TableParser(html_table)
        # parse race name and url as stage name and url and rename it afterwards
        if "race_name" in fields:
            fields[fields.index("race_name")] = "stage_name"
        if "race_url" in fields:
            fields[fields.index("race_url")] = "stage_url"
        tp.parse(fields)
        tp.rename_field("stage_name", "race_name")
        tp.rename_field("stage_url", "race_url")
        return tp.table

    def individual_wins_ranking(self, *args: str,
                                available_fields: Tuple[str, ...] = (
                                    "rank",
                                    "prev_rank",
                                    "rider_name",
                                    "rider_url",
                                    "team_name",
                                    "team_url",
                                    "nationality",
                                    "first_places",
                                    "second_places",
                                    "third_places"
                                )) -> List[Dict[str, Any]]:
        """
        Parses individual wins ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have individual wins ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "individual_wins":
            raise ExpectedParsingError(
                "This object doesn't support races_ranking method, create one"
                "with individual wins ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def teams_wins_ranking(self, *args: str,
                           available_fields: Tuple[str, ...] = (
                               "rank",
                               "prev_rank",
                               "team_name",
                               "team_url",
                               "nationality",
                               "class",
                               "first_places",
                               "second_places",
                               "third_places")) -> List[Dict[str, Any]]:
        """
        Parses teams wins ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have teams wins ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "team_wins":
            raise ExpectedParsingError(
                "This object doesn't support teams_wins_ranking method, create "
                "one with teams wins ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def nations_wins_ranking(self, *args: str,
                             available_fields: Tuple[str, ...] = (
                                 "rank",
                                 "prev_rank",
                                 "nation_name",
                                 "nation_url",
                                 "nationality",
                                 "first_places",
                                 "second_places",
                                 "third_places")) -> List[Dict[str, Any]]:
        """
        Parses nations wins ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises Exception: when object doesn't have nations wins ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "nation_wins":
            raise ExpectedParsingError(
                "This object doesn't support nations_wins_ranking method, "
                "create one with nations wins ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def dates_select(self, *args: str, avialable_fields: Tuple[str, ...] = (
            "text",
            "value")) -> List[Dict[str, str]]:
        """
        Parses dates select menu from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when dates select menu is missing
        :return: table represented as list of dicts, `value` is value to be
        put into the URL to filter by that date and `text` is the date
        """
        fields = parse_table_fields_args(args, avialable_fields)
        select_menu_html = self._select_menu_by_label("Date")
        return self._parse_select(select_menu_html, fields)

    def nations_select(self, *args: str, avialable_fields: Tuple[str, ...] = (
            "text",
            "value")) -> List[Dict[str, str]]:
        """
        Parses nations select menu from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when nations select menu is missing
        :return: table represented as list of dicts, `value` is value to be
        put into the URL to filter by that nation and `text` is the nation name
        """
        fields = parse_table_fields_args(args, avialable_fields)
        select_menu_html = self._select_menu_by_label("Nation")
        return self._parse_select(select_menu_html, fields)

    def teams_select(self, *args: str, avialable_fields: Tuple[str, ...] = (
            "text",
            "value")) -> List[Dict[str, str]]:
        """
        Parses teams select menu from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when teams select menu is missing
        :return: table represented as list of dicts, `value` is value to be
        put into the URL to filter by that team and `text` is team name
        """
        fields = parse_table_fields_args(args, avialable_fields)
        select_menu_html = self._select_menu_by_label("Team")
        return self._parse_select(select_menu_html, fields)

    def pages_select(self, *args: str, avialable_fields: Tuple[str, ...] = (
            "text",
            "value")) -> List[Dict[str, str]]:
        """
        Parses pages select menu from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when page select menu is missing
        :return: table represented as list of dicts, `value` is value to be
        put into the URL to filter that page and `text` is the page name
        """
        fields = parse_table_fields_args(args, avialable_fields)
        select_menu_html = self._select_menu_by_label("Page")
        return self._parse_select(select_menu_html, fields)

    def teamlevels_select(self, *args: str,
                          avialable_fields: Tuple[str, ...] = (
                              "text",
                              "value")) -> List[Dict[str, str]]:
        """
        Parses team levels select menu from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when team levels select menu is missing
        :return: table represented as list of dicts, `value` is value to be
        put into the URL to filter that team level and `text` is the team level
        """
        fields = parse_table_fields_args(args, avialable_fields)
        select_menu_html = self._select_menu_by_label("Teamlevel")
        return self._parse_select(select_menu_html, fields)

    def _ranking_type(self) -> Literal["individual",
                                       "nations",
                                       "teams",
                                       "races",
                                       "distance",
                                       "racedays",
                                       "individual_wins",
                                       "team_wins",
                                       "nation_wins"]:
        """
        Finds out what is the ranking type of the object based on URL

        :return: ranking type
        """
        relative_url = self.relative_url()
        if len(relative_url.split("/")) < 3 and "?" not in relative_url:
            return "individual"
        elif "races" in relative_url:
            return "races"
        elif "distance" in relative_url:
            return "distance"
        elif "racedays" in relative_url:
            return "racedays"
        elif "wins-individual" in relative_url:
            return "individual_wins"
        elif "wins-teams" in relative_url:
            return "team_wins"
        elif "wins-nations" in relative_url:
            return "nation_wins"
        elif "nations" in relative_url:
            return "nations"
        elif "teams" in relative_url:
            return "teams"
        else:
            return "individual"

    def _select_menu_by_label(self, label: str) -> Node:
        """
        Finds select menu with given label

        :param label: wanted select menu label
        :raises Exception: when select menu with that label wasn't found
        :return: HTML of wanted select menu
        """
        labels = self.html.css("ul.filter > li > .label")
        index = -1
        for i, label_html in enumerate(labels):
            if label_html.text() == label:
                index = i
        if index == -1:
            raise ExpectedParsingError(f"{label} select not in page HTML.")
        return self.html.css("li > div > select")[index]

    def _parse_regular_ranking_table(self,
            args: Tuple[str, ...],
            available_fields: Tuple[str, ...]) -> List[Dict[str, Any]]:
        """
        Does general ranking parsing procedure using TableParser.

        :param args: parsing method args
        :param available_fields: available table fields for parsing method
        :return: table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.css_first("table")
        tp = TableParser(html_table)
        tp.parse(fields)
        return tp.table

    @ staticmethod
    def _parse_select(select_menu_html: Node,
                      fields: List[str]) -> List[Dict[str, Any]]:
        """
        Uses `SelectParser` and gets parsed table

        :param select_menu_html: select menu HTML to be parsed from
        :param fields: wanted fields
        :return: table represented as list of dicts
        """
        sp = SelectParser(select_menu_html)
        sp.parse(tuple(fields))
        return sp.table
