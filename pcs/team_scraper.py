from pprint import pprint
from typing import Dict, List, Optional, Tuple, Union

from tabulate import tabulate

from scraper import Scraper
from table_parser import TableParser
from utils import parse_select_menu, parse_table_fields_args, reg


def test():
    t = Team("team/bora-hansgrohe-2022")
    print(tabulate(t.riders("rider_url")))
    # print(tabulate(t.teams_seasons_select()))
    # print(t.abbreviation())
    # print(t.bike())
    # print(t.display_name())
    # print(t.team_id())
    # print(t.season())
    # print(t.team_status())
    # print(t.team_ranking_position())
    # print(t.wins_count())
    # pprint(t.urls())
    # print(tabulate(t.riders()))


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
    _career_points_table_fields: Tuple[str, ...] = (
        "nationality",
        "rider_name",
        "rider_url",
        "points")

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
        team_url_regex = f"""
            {reg.base_url}?team{reg.team_url_str}{reg.overview}?(\\/+)?
        """
        self._validate_url(url, team_url_regex,
                           "team/bora-hansgrohe-2022")
        return self._make_absolute_url(url)

    def teams_seasons_select(self) -> List[dict]:
        """
        Parses teams seasons select menu from HTML

        :return: table with fields `text`, `value` represented as list of dicts
        """
        team_seasons_select_html = self._html.find("form > select")[0]
        return parse_select_menu(team_seasons_select_html)

    def riders(self, *args: str, available_fields: Tuple[str, ...] = (
            "nationality",
            "rider_name",
            "rider_url",
            "points",
            "age",
            "since",
            "until",
            "ranking_points",
            "ranking_position")) -> List[dict]:
        """
        Parses team riders from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table with riders represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        career_points_table_html = self._html.find("div.taba > ul.list")[0]
        tp = TableParser(career_points_table_html, "ul")
        casual_fields = [field for field in fields
                         if field in self._career_points_table_fields]
        if "rider_url" not in casual_fields:
            casual_fields.append("rider_url")
        tp.parse(casual_fields)
        table_rider_url_dict = tp.table_to_dict("rider_url")

        ages_table = self._ages_table("age" in fields, True)
        ranking_table = self._ranking_table("ranking_points" in fields,
                                            "ranking_position" in fields)
        # merge created tables to one, if age, ranking_points or ranking-
        # postition isn't in fields empty tables will be merged so nothing
        # will happen
        merged_tables = []
        for row in ranking_table:
            dict1 = {**row, **table_rider_url_dict[row['rider_url']]}
            merged_tables.append({**dict1, **ages_table[row['rider_url']]})

        # remove rider_id from table rows when it isn't in fields
        if "rider_id" not in fields:
            for row in merged_tables:
                if "rider_id" in row.keys():
                    row.pop("rider_id")
        return merged_tables

    def team_id(self) -> str:
        """
        Parses team id from URL, season is part of team id

        :return: team id e.g. `bora-hansgrohe-2022`
        """
        return self.relative_url().split("/")[1]

    def season(self) -> int:
        """
        Parses season from URL

        :return: season
        """
        team_id = self.relative_url().split("/")[1]
        season_part = team_id.split("-")[-1]
        # only first 4 characters are used because some teams might have fifth
        # character, which isn't part of season e.g. movistar-team-20152
        return int(season_part[:4])

    def display_name(self) -> str:
        """
        Parses team display name from HTML

        :return: display name e.g. `BORA - hansgrohe`
        """
        display_name_html = self._html.find(".page-title > .main > h1")[0]
        return display_name_html.text.split(" (")[0]

    def nationality(self) -> str:
        """
        Parses team's nationality from HTML

        :return: team's nationality as 2 chars long country code in uppercase
        """
        nationality_html = self._html.find(".page-title > .main > span.flag")[0]
        return nationality_html.attrs['class'][1].upper()

    def team_status(self) -> str:
        """
        Parses team status from HTML

        :return: team status as 2 chars long code in uppercase e.g. `WT` (World
        Tour)
        """
        team_status_html = self._html.find(
            "div > ul.infolist > li:nth-child(1) > div")[1]
        return team_status_html.text

    def abbreviation(self) -> str:
        """
        Parses team abbreviation from HTML

        :return: team abbreviation as 3 chars long code in uppercase e.g. `BOH`
        (BORA - hansgrohe)
        """
        abbreviation_html = self._html.find(
            "div > ul.infolist > li:nth-child(2) > div")[1]
        return abbreviation_html.text

    def bike(self) -> str:
        """
        Parses team's bike brand from HTML

        :return: bike brand e.g. `Specialized`
        """
        bike_html = self._html.find(
            "div > ul.infolist > li:nth-child(3) > div")[1]
        return bike_html.text

    def wins_count(self) -> int:
        """
        Parses count of wins in corresponding season from HTML

        :return: count of wins in corresponding season
        """
        team_ranking_html = self._html.find(
            ".teamkpi > li:nth-child(1) > div:nth-child(2)")[0]
        return int(team_ranking_html.text)

    def team_ranking_position(self) -> int:
        """
        Parses team ranking position from HTML

        :return: PCS team ranking position in corresponding year
        """
        team_ranking_html = self._html.find(
            ".teamkpi > li:nth-child(2) > div:nth-child(2)")[0]
        return int(team_ranking_html.text)

    def _ranking_table(
        self, points: bool, position: bool, as_dict: bool = False
    ) -> Union[Dict[str, dict], List[dict]]:
        """
        Parses ranking table with team riders from HTML

        :param points: whether to include ranking points to the table
        :param position: whetehr to include ranking position to the table
        :param as_dict: whether to return table as dict where rider_url is used
        as a key to each row, defaults to False
        :return: table with fields rider_url and optionaly `ranking_points` and
        `ranking` position, represented either as list of dicts or dict of dicts
        """
        ranking_table_html = self._html.find("div.tabe > ul.list")[0]
        tp = TableParser(ranking_table_html, "ul")
        tp.parse(("rider_url",))
        if points:
            tp.extend_table("ranking_points", -3,
                            lambda x: int(x.replace("(", "").replace(")", "")))
        if position:
            tp.extend_table("ranking_position", -2, lambda x: int(x))
        if as_dict:
            return tp.table_to_dict("rider_url")
        else:
            return tp.table

    def _ages_table(
        self, age: bool, as_dict: bool = False
    ) -> Union[List[dict], Dict[str, dict]]:
        """
        Parses ranking table with team riders from HTML

        :param age: whether to include riders ages to the table
        :param as_dict: whether to return table as dict where rider_url is used
        as a key to each row, defaults to False
        :return: table with fields rider_url and optionaly `ranking_points` and
        `ranking` position, represented either as list of dicts or dict of dicts
        """
        ages_html_table = self._html.find("div.tabc > ul.list")[0]
        tp = TableParser(ages_html_table, "ul")
        tp.parse(("rider_url",))
        if age:
            tp.extend_table("age", -2, int)
        if as_dict:
            return tp.table_to_dict("rider_url")
        else:
            return tp.pable


if __name__ == "__main__":
    test()
