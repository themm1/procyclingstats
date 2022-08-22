from typing import Any, Dict, List, Optional, Tuple

from selectolax.parser import HTMLParser

from .scraper import Scraper
from .table_parser2 import TableParser
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
        if self._html:
            self._html = HTMLParser(self._html.html)

    def _get_valid_url(self, url: str) -> str:
        """
        Validates given URL with regex and returns absolute URL

        :param url: URL either relative or absolute
        :raises ValueError: when URL isn't valid
        :return: absolute URL
        """
        race_startlist_url_regex = f"""
            {reg.base_url}?race{reg.url_str}
            (({reg.year}{reg.stage}{reg.startlist}{reg.anything}?)|
            ({reg.year}{reg.result}?{reg.startlist}{reg.anything}?)|
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
            "rider_number")) -> List[Dict[str, Any]]:
        """
        Parses startlist from HTML. When startlist is individual (without teams)
        fields team name, url and rider nationality are set to None.
        
        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: startlist table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        startlist_html = self._html.css_first(".startlist_v3")
        # startlist is individual startlist e.g. 
        # race/tour-de-pologne/2009/gc/startlist
        if startlist_html.css_first("li.team") is None:
            startlist_html = self._html.css_first(".page-content > div")
            startlist_table = []
            for i, rider_a in enumerate(startlist_html.css("a:not([class])")):
                startlist_table.append({})
                for field in fields:
                    startlist_table[-1][field] = None

                if "rider_url" in fields:
                    startlist_table[-1]['rider_url'] = rider_a.\
                        attributes['href']
                if "rider_name" in fields:
                    startlist_table[-1]['rider_name'] = rider_a.text()
                if "rider_number" in fields:
                    startlist_table[-1]['rider_number'] = i + 1
                if "team_name" in fields:
                    startlist_table[-1]['team_name'] = None
                if "team_url" in fields:
                    startlist_table[-1]['team_url'] = None
                if "nationality" in fields:
                    startlist_table[-1]['nationality'] = None
            return startlist_table

        casual_rider_fields = [
            "rider_name",
            "rider_url",
            "nationality"
        ]

        table = []
        for team_html in startlist_html.css("li.team"):
            riders_table = team_html.css_first("ul")
            tp = TableParser(riders_table)
            rider_f_to_parse = [f for f in casual_rider_fields if f in fields]
            tp.parse(rider_f_to_parse)
            # add rider numbers to the table if needed
            if "rider_number" in fields:
                numbers = []
                for li in riders_table.css("li"):
                    num = li.text(deep=False).split(" ")[0]
                    numbers.append(int(num))
                tp.extend_table("rider_number", numbers)
            # add team names to the table if needed
            if "team_name" in fields:
                team_name = team_html.css_first("a").text()
                team_names = [team_name for _ in range(len(tp.table))]
                tp.extend_table("team_name", team_names)
            # add team urls to the table if needed
            if "team_url" in fields:
                team_url = team_html.css_first("a").attributes['href']
                team_urls = [team_url for _ in range(len(tp.table))]
                tp.extend_table("team_url", team_urls)
            # add team table to startlist table
            table.extend(tp.table)
        return table
