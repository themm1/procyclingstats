from tracemalloc import start
from typing import List, Optional, Tuple
from xml.dom.minidom import Element

from .scraper import Scraper
from .table_parser import TableParser, TableRowParser
from .utils import parse_table_fields_args, reg


class RaceStartlist(Scraper):
    """
    Scraper for race startlist HTML page.

    :param url: URL of race overview either full or relative, e.g.
    `race/tour-de-france/2021/startlist`
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
        race_startlist_url_regex = f"""
            {reg.base_url}?race{reg.url_str}
            (({reg.year}{reg.stage}?{reg.startlist}{reg.anything}?)|
            {reg.startlist}{reg.anything}?)
            \\/*
        """
        self._validate_url(url, race_startlist_url_regex,
                           "race/tour-de-france/2022/startlist")
        return self._make_absolute_url(url)

    def startlist(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "nationality",
            "rider_number")) -> List[dict]:
        """
        Parses startlist from HTML. When startlist is individual (without teams)
        fields team name, url and rider nationality are set to None.
        
        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: startlist table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        startlist_html_table = self._html.find("ul.startlist_v3")[0]
        # parse normal startlist with teams
        if startlist_html_table.find("li"):
            return self._parse_normal_startlist(startlist_html_table, fields)
        # parse individual startlist where only rider name, url and number is
        # available
        else:
            startlist_html = self._html.find("div.page-content > div")
            return self._parse_individual_startlist(startlist_html[0], fields)
                    
    @staticmethod
    def _parse_normal_startlist(startlist_html_table: Element,
                                fields: List[str]) -> List[dict]:
        """
        Parses normal startlist (.startlist_v3)

        :param startlist_html_table: HTML of the startlist
        :param fields: fields to parse
        :return: startlist table with wanted fields as list of dicts
        """
        rider_fields = [
            field for field in fields if field in (
                "rider_name",
                "rider_url",
                "nationality",
                "rider_number")]

        startlist_table = []
        for team_html in startlist_html_table.find("li.team"):
            riders_table_html = team_html.find("ul")[0]
            tp = TableParser(riders_table_html)
            tp.parse(rider_fields)

            trp = TableRowParser(team_html)
            for row in tp.table:
                if "team_name" in fields:
                    row['team_name'] = trp.team_name()
                if "team_url" in fields:
                    row['team_url'] = trp.team_url()
            startlist_table.extend(tp.table)
        return startlist_table
        
    @staticmethod
    def _parse_individual_startlist(startlist_html: Element,
                                    fields: List[str]) -> List[dict]:
        """
        Parses individual startlist where are no teams (e.g.
        `race/tour-de-pologne/2009/startlist`)

        :param startlist_html_table: HTML of the startlist
        :param fields: fields to parse
        :return: startlist table with wanted fields as list of dicts
        """
        startlist_table = []
        for i, rider_a in enumerate(startlist_html.find("a:not([class])")):
            startlist_table.append({})
            for field in fields:
                startlist_table[-1][field] = None

            if "rider_url" in fields:
                startlist_table[-1]['rider_url'] = rider_a.attrs['href']
            if "rider_name" in fields:
                startlist_table[-1]['rider_naem'] = rider_a.text
            if "rider_number" in fields:
                startlist_table[-1]['rider_number'] = i + 1
        return startlist_table
