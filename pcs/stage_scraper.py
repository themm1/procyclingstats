from pprint import pprint
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import requests_html
from requests_html import Element
from tabulate import tabulate

from scraper import Scraper
from table_parser import TableParser
from utils import convert_date, parse_table_fields_args, reg


def test():
    # s = Stage("race/world-championship-ttt/2017")
    s = Stage("race/tour-de-france/2022/stage-3/")
    # print(tabulate(s.results()))
    # print(s.profile_icon())
    # print(tabulate(s.gc()))
    print(tabulate(s.points()))
    # print(tabulate(s.kom()))
    # print(tabulate(s.youth()))
    # print(tabulate(s.teams()))


class Stage(Scraper):
    """
    Scraper for HTML stage page. On one day races methods for parsing
    classifications (e.g. `self.gc` or `self.points`) aren't available.

    :param url: URL of race overview either full or relative, e.g.
    `race/tour-de-france/2021/stage-8`
    :param html: HTML to be parsed from, defaults to None, when passing the
    parameter, set `update_html` to False to prevent overriding or making
    useless request
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to make object ready for parsing, defaults to True
    """
    _tables_path: str = ".result-cont > table > tbody"

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
        race_stage_url_regex = f"""
            {reg.base_url}?race{reg.url_str}
            ({reg.year}{reg.stage}{reg.result}?|{reg.year})?
            (\\/+)?
        """
        self._validate_url(url, race_stage_url_regex,
                           "race/tour-de-france/2022/stage-18")
        return self._make_absolute_url(url)

    def race_season_id(self) -> str:
        """
        Parses race season id from URL

        :return: race season id e.g. `tour-de-france/2021`
        """
        return "/".join(self.relative_url().split("/")[1:3])

    def stage_id(self) -> str:
        """
        Parses stage id from URL

        :returns: stage id e.g. `tour-de-france/2021/stage-9`
        """
        url_elements = self.relative_url().split("/")[1:]
        stage_id = [element for element in url_elements if element != "result"]
        return "/".join(stage_id)

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is an one day race from HTML

        :return: whether the race is an one day race
        """
        # If there are elements with .restabs class (Stage/GC... menu), the race
        # is a stage race
        return len(self._html.find(".restabs")) == 0

    def distance(self) -> float:
        """
        Parses stage distance from HTML

        :return: stage distance in kms
        """
        distance_html = self._html.find(".infolist > li:nth-child(5) > div")
        return float(distance_html[1].text.split(" km")[0])

    def profile_icon(self) -> Literal["p0", "p1", "p2", "p3", "p4", "p5"]:
        """
        Parses profile icon from HTML

        :return: profile icon e.g. `p4`, the higher the number is the more
        difficult the profile is
        """
        profile_html = self._html.find(".infolist > li:nth-child(7) > "
                                       "div:nth-child(2) > span")
        return profile_html[0].attrs['class'][2]

    def stage_type(self) -> Literal["ITT", "TTT", "RR"]:
        """
        Parses stage type from HTML

        :return: stage type
        """
        stage_name_html = self._html.find(".sub > .blue")
        stage_name2_html = self._html.find("div.main > h1")[0]
        stage_name = stage_name_html[0].text
        stage_name2 = stage_name2_html.text
        if "ITT" in stage_name or "ITT" in stage_name2:
            return "ITT"
        elif "TTT" in stage_name or "TTT" in stage_name2:
            return "TTT"
        else:
            return "RR"

    def winning_attack_length(self, when_none_or_unknown: float = 0.0) -> float:
        """
        Parses length of winning attack from HTML

        :param when_none_or_unknown: value to return when there is no info
        about winning attack, defaults to 0.0
        :return: length of winning attack"""
        won_how_html = self._html.find(".infolist > li:nth-child(12) > div")
        won_how = won_how_html[1].text
        if " km solo" in won_how:
            return float(won_how.split(" km sol")[0])
        else:
            return when_none_or_unknown

    def vertical_meters(self) -> int:
        """
        Parses vertical meters gained throughout the stage from HTML

        :return: vertical meters
        """
        vertical_meters_html = self._html.find(".infolist > li:nth-child(9) "
                                               " > div")
        vertical_meters = vertical_meters_html[1].text
        return int(vertical_meters) if vertical_meters else None

    def date(self) -> str:
        """
        Parses date when stage took place from HTML

        :return: date when stage took place `yyyy-mm-dd`
        """
        date_html = self._html.find(f".infolist > li > div")
        date = date_html[1].text.split(", ")[0]
        return convert_date(date)

    def departure(self) -> str:
        """
        Parses departure of the stage from HTML

        :return: departure of the stage
        """
        departure_html = self._html.find(".infolist > li:nth-child(10) > div")
        return departure_html[1].text

    def arrival(self) -> str:
        """
        Parses arrival of the stage from HTML

        :return: arrival of the stage
        """
        arrival_html = self._html.find(".infolist > li:nth-child(11) > div")
        return arrival_html[1].text

    def results(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "status",
            "age",
            "nationality",
            "time",
            "bonus",
            "pcs_points",
            "uci_points")) -> List[dict]:
        """
        Parses main results table from HTML, if results table is TTT one day
        race, fields `age`, `nationality` and `bonus` are not available

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises Exception: when one day race TTT results table had invalid
        fields
        :return: results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        # because of one day races self._table_index isn't used here
        categories = self._html.find(self._tables_path)
        results_table_html = categories[0].html
        # parse TTT table
        if self.stage_type() == "TTT":
            tp = TableParser(results_table_html)
            wanted_ttt_fields = [field for field in fields if field in
                                 tp.ttt_fields]
            # add rider_url for easier parsing
            rider_url_added = False
            if "rider_url" not in wanted_ttt_fields:
                wanted_ttt_fields.append("rider_url")
                rider_url_added = True

            tp.parse_ttt_table(wanted_ttt_fields)
            rider_url_key_table = {row['rider_url']: row for row in tp.table}
            # remove rider_url from table
            if rider_url_added:
                for rider_url in rider_url_key_table.keys():
                    rider_url_key_table[rider_url].pop("rider_url")

            wanted_extra_fields = [field for field in fields if field not in
                                   tp.ttt_fields]
            if wanted_extra_fields and self.is_one_day_race():
                raise Exception(
                    "Can't parse nationality or age of TTT results "
                    "table participant, when race is an one day race.")
            elif wanted_extra_fields and not self.is_one_day_race():
                gc_table_html = self._table_html("gc")
                extra_tp = TableParser(gc_table_html)
                wanted_extra_fields.append("rider_url")
                extra_tp.parse(wanted_extra_fields)
                # merge tp.table and extra_tp.table by rider_url and remove
                # rider_url from extra_tp.table
                table = []
                for row in extra_tp.table:
                    row2 = rider_url_key_table[row['rider_url']]
                    row.pop("rider_url")
                    table.append({**row, **row2})
                return table
            else:
                return tp.table
        else:
            tp = TableParser(results_table_html)
            tp.parse(fields)
            tp.make_times_absolute()
            return tp.table

    def gc(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "age",
            "nationality",
            "time",
            "bonus",
            "pcs_points",
            "uci_points")) -> List[dict]:
        """
        Parses results from GC results table from HTML, available only on stage
        races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: GC results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        gc_table_html = self._table_html("gc")
        tp = TableParser(gc_table_html)
        tp.parse(fields)
        tp.make_times_absolute()
        return tp.table

    def points(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "points",
            "age",
            "nationality",
            "pcs_points",
            "uci_points")) -> List[dict]:
        """
        Parses results from points classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: points classification results table represented as list of
        dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        points_table_html = self._table_html("points")
        tp = TableParser(points_table_html)
        tp.parse(fields)
        return tp.table

    def kom(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "points",
            "age",
            "nationality",
            "pcs_points",
            "uci_points")) -> List[dict]:
        """
        Parses results from KOM classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: KOM classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        kom_table_html = self._table_html("kom")
        tp = TableParser(kom_table_html)
        tp.parse(fields)
        return tp.table

    def youth(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "time",
            "age",
            "nationality",
            "pcs_points",
            "uci_points")) -> List[dict]:
        """
        Parses results from youth classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: youth classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        youth_table_html = self._table_html("youth")
        tp = TableParser(youth_table_html)
        tp.parse(fields)
        tp.make_times_absolute()
        return tp.table

    def teams(self, *args: str, available_fields: Tuple[str, ...] = (
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "time",
            "nationality",
            "pcs_points",
            "uci_points")) -> List[dict]:
        """
        Parses results from teams classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: youth classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        teams_table_html = self._table_html("teams")
        tp = TableParser(teams_table_html)
        tp.parse(fields)
        tp.make_times_absolute()
        return tp.table

    def _table_html(self, table: Literal[
            "stage",
            "gc",
            "points",
            "kom",
            "youth",
            "teams"]) -> Optional[Element]:
        """
        Get HTML of a .result-cont table with results based on `table` param

        :param table: keyword of wanted table that occures in .restabs menu
        :return: HTML of wanted HTML table, None when not found
        """
        categories = self._html.find(".result-cont")
        for i, element in enumerate(self._html.find("ul.restabs > li > a")):
            if table in element.text.lower():
                return categories[i].find("tbody")[0]

    def _points_index(self, html: requests_html.HTML) -> Union[int, None]:
        """
        Get index of column with points from HTML table

        :param html: HTML table to be parsed from
        :return: index of columns with points, None when not found
        """
        points_index = None
        elements = html.find("tbody > tr:first-child > td")
        for i, element in enumerate(reversed(elements)):
            if element.text.isnumeric():
                points_index = len(elements) - i
                break
        return points_index


if __name__ == "__main__":
    test()
