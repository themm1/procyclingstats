from pprint import pprint
from typing import Any, Dict, List, Literal, Union

import requests_html
from requests_html import HTML
from tabulate import tabulate

from parsers import TableParser, TableRowParser, parse_ttt_table
from race_scraper import Race
from scraper import Scraper
from utils import convert_date, parse_table_fields_args


def test():
    s = Stage("race/milano-sanremo")
    s.parse_html()
    print(tabulate(s.results()))
    # print(tabulate(s.gc()))
    # print(tabulate(s.points()))
    # print(tabulate(s.kom()))
    # print(tabulate(s.youth()))
    # print(tabulate(s.teams()))


class Stage(Scraper):
    _course_translator = {
        "p0": (None, None),
        "p1": ("flat", 0),
        "p2": ("hilly", 0),
        "p3": ("hilly", 1),
        "p4": ("mountain", 0),
        "p5": ("mountain", 1),
    }
    _tables_path = ".result-cont > table > tbody"

    def __init__(self, stage_url: str, print_request_url: bool = False) -> None:
        """
        Creates Stage object ready for HTML parsing

        :param race_url: URL of race overview either full or relative, e.g.\
            `race/tour-de-france/2021/stage-8`
        :param print_request_url: whether to print URL when making request,\
            defaults to False
        """
        Race._validate_url(stage_url, stage_url)
        super().__init__(stage_url, print_request_url)

    def parse_html(self) -> Dict[str, Any]:
        """
        Stores all parsable info to `self.content` dict

        :return: `self.content` dict
        """
        self.content['info'] = {
            "stage_id": self.stage_id(),
            "race_season_id": self.race_season_id(),
            "distance": self.distance(),
            "mtf": self.mtf(),
            "course_type": self.course_type(),
            "race_type": self.stage_type(),
            "winning_attack_length": self.winning_attack_length(),
            "vertical_meters": self.vertical_meters(),
            "date": self.date(),
            "departure": self.departure(),
            "arrival": self.arrival()
        }
        self.content['results'] = self.results()
        # When the race is stage race, add classifications
        if self.is_stage_race():
            self.content['gc'] = self.gc()
            self.content['points'] = self.points()
            self.content['kom'] = self.kom()
            self.content['youth'] = self.youth()
            self.content['teams'] = self.teams()
        return self.content

    def race_season_id(self) -> str:
        """
        Parses race season id from URL

        :return: race season id e.g. `tour-de-france/2021`
        """
        return "/".join(self._cut_base_url().split("/")[1:3])

    def stage_id(self) -> str:
        """
        Parses stage id from URL

        :returns: stage id e.g. `tour-de-france/2021/stage-9`
        """
        url_elements = self._cut_base_url().split("/")[1:]
        stage_id = [element for element in url_elements if element != "result"]
        return "/".join(stage_id)

    def is_stage_race(self) -> bool:
        """
        Parses whether race is a stage race from HTML

        :return: whether the race is a stage race
        """
        # If there are elements with .restabs class (Stage/GC... menu), the race
        # is a stage race
        return len(self.html.find(".restabs")) > 0

    def distance(self) -> float:
        """
        Parses stage distance from HTML

        :return: stage distance in kms
        """
        distance_html = self.html.find(".infolist > li:nth-child(5) > div")
        return float(distance_html[1].text.split(" km")[0])

    def mtf(self) -> bool:
        """
        Parses whether stage has mountain finnish

        :return: whether stage has mtf
        """
        profile_html = self.html.find(".infolist > li:nth-child(7) > \
            div:nth-child(2) > span")
        profile = profile_html[0].attrs['class'][2]
        return bool(self._course_translator[profile][1])

    def course_type(self) -> Union[Literal["flat", "hilly", "mountain"], None]:
        """
        Parses course type from HTML

        :return: course type
        """
        profile_html = self.html.find(".infolist > li:nth-child(7) > \
            div:nth-child(2) > span")
        profile = profile_html[0].attrs['class'][2]
        return self._course_translator[profile][0]

    def stage_type(self) -> Literal["itt", "ttt", "rr"]:
        """
        Parses stage type from HTML

        :return: stage type
        """
        stage_name_html = self.html.find(".sub > .blue")
        stage_name = stage_name_html[0].text
        if "(ITT)" in stage_name:
            return "itt"
        elif "(TTT)" in stage_name:
            return "ttt"
        else:
            return "rr"

    def winning_attack_length(self, when_none_or_unknown: float = 0.0) -> float:
        """
        Parses length of winning attack from HTML

        :param when_none_or_unknown: value to return when there is no info \
            about winning attack, defaults to 0.0
        :return: length of winning attack"""
        won_how_html = self.html.find(".infolist > li:nth-child(12) > div")
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
        vertical_meters_html = self.html.find(".infolist > li:nth-child(9) \
            > div")
        vertical_meters = vertical_meters_html[1].text
        return int(vertical_meters) if vertical_meters else None

    def date(self) -> str:
        """
        Parses date when stage took place from HTML

        :return: date when stage took place `yyyy-mm-dd`
        """
        date_html = self.html.find(f".infolist > li > div")
        date = date_html[1].text.split(", ")[0]
        return convert_date(date)

    def departure(self) -> str:
        """
        Parses departure of the stage from HTML

        :return: departure of the stage
        """
        departure_html = self.html.find(".infolist > li:nth-child(10) > div")
        return departure_html[1].text

    def arrival(self) -> str:
        """
        Parses arrival of the stage from HTML

        :return: arrival of the stage
        """
        arrival_html = self.html.find(".infolist > li:nth-child(11) > div")
        return arrival_html[1].text

    def results(self, *args: str, fields: tuple = (
                "rider_name", "rider_url", "team_name", "team_url", "rank",
                "status", "age", "nationality", "time", "bonus", "pcs_points",
                "uci_points")) -> List[dict]:
        """
        Parses main results table from HTML

        :param *args: fields that should be contained in results table,\
            available options are a all included in `fields` default value
        :param fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, fields)
        # remove other result tables from html
        # because of one day races self._table_index isn't used here
        categories = self.html.find(self._tables_path)
        results_table_html = HTML(html=categories[0].html)
        if self.stage_type() == "ttt":
            gc_table_html = self._table_html("gc")
            return parse_ttt_table(results_table_html, fields, gc_table_html)
        else:
            tp = TableParser(results_table_html)
            tp.parse(fields)
            tp.make_times_absolute()
            return tp.table

    def gc(self, *args: str, fields: tuple = (
        "rider_name", "rider_url", "team_name", "team_url", "rank", "prev_rank",
        "age", "nationality", "time", "bonus", "pcs_points", "uci_points"
    )) -> List[dict]:
        """
        Parses results from GC results table from HTML, available only on stage\
            races

        :param *args: fields that should be contained in results table,\
            available options are a all included in `fields` default value
        :param fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: GC results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, fields)
        # remove other result tables from html
        gc_table_html = self._table_html("gc")
        tp = TableParser(gc_table_html)
        tp.parse(fields)
        tp.make_times_absolute()
        return tp.table

    def points(self, *args: str, fields: tuple = (
        "rider_name", "rider_url", "team_name", "team_url", "rank", "prev_rank",
        "points", "age", "nationality", "pcs_points", "uci_points"
    )) -> List[dict]:
        """
        Parses results from points classification results table from HTML,\
            available only on stage races

        :param *args: fields that should be contained in results table,\
            available options are a all included in `fields` default value
        :param fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: points classification results table represented as list of\
            dicts
        """
        fields = parse_table_fields_args(args, fields)
        # remove other result tables from html
        points_table_html = self._table_html("points")
        tp = TableParser(points_table_html)
        tp.parse(fields)
        return tp.table

    def kom(self, *args: str, fields: tuple = (
        "rider_name", "rider_url", "team_name", "team_url", "rank", "prev_rank",
        "points", "age", "nationality", "pcs_points", "uci_points"
    )) -> List[dict]:
        """
        Parses results from KOM classification results table from HTML,\
            available only on stage races

        :param *args: fields that should be contained in results table,\
            available options are a all included in `fields` default value
        :param fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: KOM classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, fields)
        # remove other result tables from html
        kom_table_html = self._table_html("kom")
        tp = TableParser(kom_table_html)
        tp.parse(fields)
        return tp.table

    def youth(self, *args: str, fields: tuple = (
        "rider_name", "rider_url", "team_name", "team_url", "rank", "prev_rank",
        "time", "age", "nationality", "pcs_points", "uci_points"
    )) -> List[dict]:
        """
        Parses results from youth classification results table from HTML,\
            available only on stage races

        :param *args: fields that should be contained in results table,\
            available options are a all included in `fields` default value
        :param fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: youth classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, fields)
        youth_table_html = self._table_html("youth")
        tp = TableParser(youth_table_html)
        tp.parse(fields)
        tp.make_times_absolute()
        return tp.table

    def teams(self, *args: str, fields: tuple = (
        "team_name", "team_url", "rank", "prev_rank", "time", "nationality",
            "pcs_points", "uci_points")) -> List[dict]:
        """
        Parses results from teams classification results table from HTML,\
            available only on stage races

        :param *args: fields that should be contained in results table,\
            available options are a all included in `fields` default value
        :param fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: youth classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, fields)
        teams_table_html = self._table_html("teams")
        tp = TableParser(teams_table_html)
        tp.parse(fields)
        tp.make_times_absolute()
        return tp.table

    def _table_html(self, table: Literal["stage", "gc", "points", "kom",
                    "youth", "teams"]) -> Union[HTML, None]:
        """
        Get HTML of a .result-cont table with results based on `table` param

        :param table: keyword of wanted table that occures in .restabs menu
        :return: HTML of wanted HTML table, None when not found
        """
        categories = self.html.find(".result-cont")
        for i, element in enumerate(self.html.find("ul.restabs > li > a")):
            if table in element.text.lower():
                return HTML(html=categories[i].find("tbody")[0].html)

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
