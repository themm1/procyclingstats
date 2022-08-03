from cgitb import html
from typing import List, Literal, Tuple

from requests_html import HTML
from tabulate import tabulate

from scraper import Scraper
from select_parser import SelectParser
from table_parser import TableParser
from utils import parse_table_fields_args


def test():
    r = Ranking("rankings/me")
    d = r.nations_select()
    print(tabulate(d))


class Ranking(Scraper):
    """
    Scraper for HTML ranking page. Always only one method for ranking
    parsing is available (based on ranking type). e.g. `self.individual_ranking`
    for `rankings/me/season-individual` ranking

    :param url: URL of ranking to be parsed from, either full or relative,
    e.g. `rankings/me/season-individual` or 'rankings.php?date=2021-12-31&
    nation=&age=&zage=&page=smallerorequal&team=&offset=0&filter=Filter&p=me
    &s=season-individual'
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to make object ready for parsing, defaults to True
    """

    def __init__(self, url: str, update_html: bool = False) -> None:
        self._validate_url(url)
        super().__init__(url, update_html)

    def individual_ranking(self, *args: str,
                           available_fields: Tuple[str, ...] = (
                               "rank",
                               "prev_rank",
                               "rider_name",
                               "rider_url",
                               "team_name",
                               "team_url",
                               "nationality",
                               "points")) -> List[dict]:
        """
        Parses individual ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have individual ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "individual":
            raise Exception(
                "This object doesn't support individual_ranking method, create"
                "one with individual ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.find("table > tbody")[0]
        tp = TableParser(html_table)
        tp.parse(fields)
        return tp.table

    def team_ranking(self, *args: str, available_fields: Tuple[str, ...] = (
            "rank",
            "prev_rank",
            "team_name",
            "team_url",
            "nationality",
            "class",
            "points")) -> List[dict]:
        """
        Parses team ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have teams ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "teams":
            raise Exception(
                "This object doesn't support team_ranking method, "
                "create one with teams ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.find("table > tbody")[0]
        tp = TableParser(html_table)
        tp.parse([field for field in fields if field != "class"])
        if "class" in fields:
            # extend table to contain class (e.g. WT) if needed
            tp.extend_table("class", -2, str)
        return tp.table

    def nations_ranking(self, *args: str, available_fields: Tuple[str, ...] = (
            "rank",
            "prev_rank",
            "nation_name",
            "nation_url",
            "nationality",
            "points")) -> List[dict]:
        """
        Parses nations ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have nations ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "nations":
            raise Exception(
                "This object doesn't support nations_ranking method, create one"
                "with nations ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.find("table > tbody")[0]
        tp = TableParser(html_table)
        tp.parse(fields)
        return tp.table

    def races_ranking(self, *args: str, available_fields: Tuple[str, ...] = (
            "rank",
            "prev_rank",
            "race_name",
            "race_url",
            "nationality",
            "class",
            "points")) -> List[dict]:
        """
        Parses races ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have races ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "races":
            raise Exception(
                "This object doesn't support races_ranking method, create one"
                "with race ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.find("table > tbody")[0]
        tp = TableParser(html_table)
        tp.parse([field for field in fields if field != "class"])
        if "class" in fields:
            # extend table to contain class (e.g. 2.UWT) if needed
            tp.extend_table("class", -2, str)
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
                                )) -> List[dict]:
        """
        Parses individual wins ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have individual wins ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "individual_wins":
            raise Exception(
                "This object doesn't support races_ranking method, create one"
                "with individual wins ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.find("table > tbody")[0]
        tp = TableParser(html_table)
        casual_fields = [
            field for field in fields
            if field != "first_places" and field != "second_places" and field
            != "third_places"]
        tp.parse(casual_fields)
        self._extend_table_to_podiums(tp, fields)
        return tp.table

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
                               "third_places")) -> List[dict]:
        """
        Parses teams wins ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when object doesn't have teams wins ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "team_wins":
            raise Exception(
                "This object doesn't support teams_wins_ranking method, create "
                "one with teams wins ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.find("table > tbody")[0]
        tp = TableParser(html_table)
        casual_fields = [
            field for field in fields
            if field != "first_places" and field != "second_places" and field
            != "third_places" and field != "class"]
        tp.parse(casual_fields)
        if "class" in fields:
            tp.extend_table("class", -4, str)
        self._extend_table_to_podiums(tp, fields, [-3, -2, -1])
        return tp.table

    def nations_wins_ranking(self, *args: str,
                             available_fields: Tuple[str, ...] = (
                                 "rank",
                                 "prev_rank",
                                 "nation_name",
                                 "nation_url",
                                 "nationality",
                                 "first_places",
                                 "second_places",
                                 "third_places")) -> List[dict]:
        """
        Parses nations wins ranking from HTML

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises Exception: when object doesn't have nations wins ranking URL
        :return: table represented as list of dicts
        """
        if self._ranking_type() != "nation_wins":
            raise Exception(
                "This object doesn't support nations_wins_ranking method, "
                "create one with nations wins ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.find("table > tbody")[0]
        tp = TableParser(html_table)
        casual_fields = [
            field for field in fields
            if field != "first_places" and field != "second_places" and field
            != "third_places"]
        tp.parse(casual_fields)
        self._extend_table_to_podiums(tp, fields)
        return tp.table

    def dates_select(self, *args: str, avialable_fields: Tuple[str, ...] = (
            "text",
            "value")) -> List[dict]:
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
            "value")) -> List[dict]:
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
            "value")) -> List[dict]:
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
            "value")) -> List[dict]:
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
                              "value")) -> List[dict]:
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
        if len(relative_url.split("/")) < 3:
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
        elif "nation" in relative_url:
            return "nations"
        elif "team" in relative_url:
            return "teams"
        else:
            return "individual"

    def _validate_url(self, url: str):
        """
        Checks whether given URL is valid before making request

        :param url: URL to check
        :raises ValueError: when given URL is invalid
        """
        url_to_check = url.split("/")
        for element in reversed(url_to_check):
            if element != "":
                break
            url_to_check.pop()

        if "https" in url:
            if self.base_url != "/".join(url_to_check[:3]) + "/":
                raise ValueError(f"Invalid URL: {url}")
            url_to_check = url_to_check[3:]
        valid = url_to_check[0] == "rankings"
        if len(url_to_check) > 1 and valid:
            valid = url_to_check[1] == "me" or\
                url_to_check[1] == "we" or\
                url_to_check[1] == "mj"
        if not valid:
            raise ValueError(f"Invalid URL: {url}")

    def _select_menu_by_label(self, label: str) -> HTML:
        """
        Finds select menu with given label

        :param label: wanted select menu label
        :raises Exception: when select menu with that label wasn't found
        :return: HTML of wanted select menu
        """
        labels = self.html.find("ul.filter > li > .label")
        index = -1
        for i, label_html in enumerate(labels):
            if label_html.text == label:
                index = i
        if index == -1:
            raise Exception(f"Invalid label: {label}")
        return self.html.find("li > div > select")[index]

    @staticmethod
    def _extend_table_to_podiums(tp: TableParser, fields: List[str],
                                 podium_indexes: List[int] = [-4, -3, -2]
                                 ) -> None:
        """
        Extends table to podiums from HTML wins table

        :param tp: `TableParser` object with table to extend
        :param fields: wanted table fields
        :param podium_indexes: list with indexes to `td` elements with podium
        positions counts
        """
        if "first_places" in fields:
            tp.extend_table("first_places", podium_indexes[0],
                            lambda x: int(x) if x != "-" else 0)
        if "second_places" in fields:
            tp.extend_table("second_places", podium_indexes[1],
                            lambda x: int(x) if x != "-" else 0)
        if "third_places" in fields:
            tp.extend_table("third_places", podium_indexes[2],
                            lambda x: int(x) if x != "-" else 0)

    @ staticmethod
    def _parse_select(select_menu_html: HTML, fields: List[str]) -> List[dict]:
        """
        Uses `SelectParser` and gets parsed table

        :param select_menu_html: select menu HTML to be parsed from
        :param fields: wanted fields
        :return: table represented as list of dicts
        """
        sp = SelectParser(select_menu_html)
        sp.parse(fields)
        return sp.table


if __name__ == "__main__":
    test()
