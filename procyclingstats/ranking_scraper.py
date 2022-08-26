from typing import Any, Dict, List, Literal, Tuple, Union

from selectolax.parser import HTMLParser

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import (format_url_filter, parse_select, parse_table_fields_args,
                    reg, select_menu_by_label)


class Ranking(Scraper):
    """
    Scraper for rankings HTML page. Example URL: `rankings/me/individual`.
    
    Always only one parsing method that parses ranking is availabe, the others
    raise `ExpectedParsingError`. E.g. for object created with example URL
    would be valid only `self.individual_ranking` parsing method and others
    methods that parse ranking (`self.team_ranking`, ...) would raise error.
    """

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

    @staticmethod
    def _html_invalid(html: HTMLParser) -> bool:
        """
        Overrides `Scraper` method. HTML is considered invalid when 'Due to
        technical difficulties this page is temporarily unavailable.' is
        contained in HTML page content.

        :param html: HTML to validate
        :return: True if given HTML is invalid, otherwise False
        """
        page_title = html.css_first("div.page-content > div").text()
        invalid_str = ("Due to technical difficulties this page is " +
        "temporarily unavailable.")
        return page_title == invalid_str

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
        decomposed_url = self._decompose_url()
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

    def dates_select(self) -> List[Dict[str, str]]:
        """
        Parses dates select menu from HTML.
        
        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        select_menu_html = select_menu_by_label(self.html, "Date")
        return parse_select(select_menu_html)

    def nations_select(self) -> List[Dict[str, str]]:
        """
        Parses nations select menu from HTML.
        
        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        select_menu_html = select_menu_by_label(self.html, "Nation")
        return parse_select(select_menu_html)

    def teams_select(self) -> List[Dict[str, str]]:
        """
        Parses teams select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        select_menu_html = select_menu_by_label(self.html, "Team")
        return parse_select(select_menu_html)

    def pages_select(self) -> List[Dict[str, str]]:
        """
        Parses pages select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        select_menu_html = select_menu_by_label(self.html, "Page")
        return parse_select(select_menu_html)

    def teamlevels_select(self) -> List[Dict[str, str]]:
        """
        Parses team levels select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        select_menu_html = select_menu_by_label(self.html, "Teamlevel")
        return parse_select(select_menu_html)

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
