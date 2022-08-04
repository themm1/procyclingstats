from pprint import pprint
from typing import Any, Dict, List, Literal, Optional, Tuple

from requests_html import HTML
from tabulate import tabulate

from scraper import Scraper
from table_parser import TableParser
from utils import parse_table_fields_args, reg


def test():
    # RaceOverview()
    url = "https://www.procyclingstats.com/race/tour-de-france/2022/gc/overview"
    race = RaceOverview(url)
    print(tabulate(race.stages()))
    # print(race.startdate())
    # pprint(race.stages())

    # stages = RaceStages(url)

    # startlist = RaceStartlist(url + "/startlist")
    # print(tabulate(startlist.startlist()))


class RaceOverview(Scraper):
    """
    Scraper for race overview page.

    :param url: URL of race overview either full or relative, e.g.
    `race/tour-de-france/2021/overview`
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
        race_url_overview_regex = f"""
            {reg.base_url}?race{reg.url_str}
            ({reg.year}{reg.stage}{reg.overview}|{reg.year}{reg.overview})
            (\\/+)?
        """
        self._validate_url(url, race_url_overview_regex,
                           "race/tour-de-france/2021/overview")
        return self._make_absolute_url(url)

    def race_id(self) -> str:
        """
        Parses race id from URL

        :return: race id e.g. `tour-de-france`
        """
        return self.relative_url().split("/")[1]

    def year(self) -> int:
        """
        Parses year when the race occured from URL

        :return: year as int
        """
        return int(self.relative_url().split("/")[2])

    def display_name(self) -> str:
        """
        Parses display name from HTML

        :return: display name e.g. `Tour de France`
        """
        display_name_html = self._html.find(".page-title > .main > h1")[0]
        return display_name_html.text

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is one day race from HTML

        :return: whether given race is one day race
        """
        one_day_race_html = self._html.find("div.sub > span.blue")[0]
        return "stage" not in one_day_race_html.text.lower()

    def nationality(self) -> str:
        """
        Parses race nationality from HTML

        :return: 2 chars long country code
        """
        nationality_html = self._html.find(".page-title > .main > span")[0]
        return nationality_html.attrs['class'][1].upper()

    def race_year(self) -> int:
        """
        Parses race ridden year from HTML

        :return: race ridden year
        """
        race_year_html = self._html.find(".page-title > .main > font")[0]
        return int(race_year_html.text[:-2])

    def startdate(self) -> str:
        """
        Parses race startdate from HTML

        :return: startdate in `dd-mm-yyyy` format
        """
        startdate_html = self._html.find(".infolist > li > div:nth-child(2)")[0]
        return startdate_html.text

    def enddate(self) -> str:
        """
        Parses race enddate from HTML

        :return: enddate in `dd-mm-yyyy` format
        """
        enddate_html = self._html.find(".infolist > li > div:nth-child(2)")[1]
        return enddate_html.text

    def category(self) -> str:
        """
        Parses race category from HTML

        :return: race category e.g. `Men Elite`
        """
        category_html = self._html.find(".infolist > li > div:nth-child(2)")[2]
        return category_html.text

    def uci_tour(self) -> str:
        """
        Parses UCI Tour of the race from HTML

        :return: UCI Tour of the race e.g. `UCI Worldtour`
        """
        uci_tour_html = self._html.find(".infolist > li > div:nth-child(2)")[3]
        return uci_tour_html.text

    def stages(self, *args: str, available_fields: Tuple[str, ...] = (
            "date",
            "profile_icon",
            "stage_name",
            "stage_url",
            "distance")) -> List[dict]:
        """
        Parses race stages from HTML (available only on stage races)

        :param *args: fields that should be contained in results table,
        available options are a all included in `fields` default value
        :param available_fields: default fields, all available options
        :raises Exception: when race is one day race
        :return: table with wanted fields represented as list of dicts
        """
        if self.is_one_day_race():
            raise Exception("This method is available only on stage races")
        fields = parse_table_fields_args(args, available_fields)
        stages_table_html = self._html.find("div:nth-child(3) > ul.list")[0]
        tp = TableParser(stages_table_html, "ul")
        tp.parse(fields, lambda x: True if "Restday" in x.text else False)
        tp.add_year_to_dates(self.year())
        return tp.table


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
        race_url_overview_regex = f"""
            {reg.base_url}?race{reg.url_str}
            ({reg.year}{reg.stage}{reg.overview}|{reg.year}{reg.overview})
            (\\/+)?
        """
        self._validate_url(url, race_url_overview_regex,
                           "race/tour-de-france/2022/startlist")
        return self._make_absolute_url(url)

    def race_id(self) -> str:
        """
        Parses race id from URL

        :return: race id e.g. `tour-de-france`
        """
        return self.relative_url().split("/")[1]

    def year(self) -> int:
        """
        Parses year when the race occured from URL

        :return: year as int
        """
        return int(self.relative_url().split("/")[2])

    def teams(self) -> List[str]:
        """
        Parses teams ids from HTML

        :return: list with team ids
        """
        teams_html = self._html.find("ul > li.team > b > a")
        return [team.attrs['href'].split("/")[1] for team in teams_html]

    def startlist(self) -> List[dict]:
        """
        Parses startlist from HTML

        :return: table with columns `rider_id`, `rider_number`, `team_id`
        represented as list of dicts
        """
        startlist = []
        teams_html = self._html.find("ul > li.team")
        for team_html in teams_html:
            # create new HTML object from team_html
            current_html = HTML(html=team_html.html)
            team_id_html = current_html.find("b > a")
            riders_ids_html = current_html.find("div > ul > li > a")
            riders_numbers_html = current_html.find("div > ul > li")

            zipped_htmls = zip(riders_ids_html, riders_numbers_html)
            team_id = team_id_html[0].attrs['href'].split("/")[1]

            # loop through riders from the team
            for id_html, number_html in zipped_htmls:
                rider_number = int(number_html.text.split(" ")[0])
                rider_id = id_html.attrs['href'].split("/")[1]
                startlist.append({
                    "rider_id": rider_id,
                    "team_id": team_id,
                    "rider_number": rider_number
                })
        return startlist


if __name__ == "__main__":
    test()
