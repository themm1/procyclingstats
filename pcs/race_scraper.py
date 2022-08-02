from pprint import pprint
from typing import Any, Dict, List, Literal, Tuple

from requests_html import HTML
from tabulate import tabulate

from scraper import Scraper
from table_parser import TableParser
from utils import course_translator, parse_table_fields_args


def test():
    # RaceOverview()
    url = "race/tour-de-france/2021"
    race = RaceOverview(url + "/overview")
    print(tabulate(race.stages()))
    # print(race.startdate())
    # pprint(race.stages())
    # race.parse_html()
    # pprint(race.content)

    # stages = RaceStages(url)
    # stages.parse_html()
    # pprint(stages.content)

    # startlist = RaceStartlist(url + "/startlist")
    # startlist.parse_html()
    # print(tabulate(startlist.startlist()))


class Race(Scraper):
    def __init__(self, race_url: str, update_html: bool = True) -> None:
        """
        General Race class

        :param race_url: URL of the race, e.g. `race/tour-de-france/2021`
        :param update_html: whether to make request to given URL and update
        `self.html`, when False `self.update_html` method has to be called
        manually to make object ready for parsing, defaults to True
        """
        super().__init__(race_url, update_html)

    def _validate_url(
        self, url: str, extra: Literal["", "overview", "startlist"] = ""
    ) -> None:
        """
        Checks whether given URL is valid before making request, is used by
        `Stage` class too

        :param url: race URL to be validate e.g. `race/tour-de-france/2021`
        :param extra: string that should URL contain after regular race URL e.g.
        `overview`
        :param stage: whether given URL is stage URL
        :raises ValueError: when URL is invalid
        """
        url_to_check = url.split("/")
        # remove empty strings from URL end (race/tour-de-france/2022/stage-19/)
        for element in reversed(url_to_check):
            if element != "":
                break
            url_to_check.pop()
        try:
            # remove self.base_url from URL if needed
            if "https" in url:
                if self.base_url != "/".join(url_to_check[:3]) + "/":
                    raise IndexError()
                url_to_check = url_to_check[3:]
            length = 4 if extra else 3
            # check criteria of valid URL
            valid = len(url_to_check) >= 2 and \
                len(url_to_check) <= 4 and \
                url_to_check[0] == "race"
            if valid and len(url_to_check) > 2:
                valid = url_to_check[2].isnumeric() and \
                    len(url_to_check[2]) == 4
            if extra and valid:
                valid = url_to_check[-1] == extra
            if not valid:
                raise ValueError(f"Invalid URL: {url}")
        # if criteria couldn't been checked URL is invalid
        except IndexError:
            raise ValueError(f"Invalid URL: {url}")

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

    def race_season_id(self) -> str:
        """
        Parses race seson id from URL

        :return: race season id e.g. `tour-de-france/2021`
        """
        return "/".join(self.relative_url().split("/")[1:3])


class RaceOverview(Race):
    _course_translator: dict = course_translator

    def __init__(self, url: str, update_html: bool = True) -> None:
        """
        Creates RaceOverview object ready for HTML parsing

        :param url: URL of race overview either full or relative, e.g.
        `race/tour-de-france/2021/overview`
        :param update_html: whether to make request to given URL and update
        `self.html`, when False `self.update_html` method has to be called
        manually to make object ready for parsing, defaults to True
        """
        self._validate_url(url, "overview")
        super().__init__(url, update_html)

    def parse_html(self) -> Dict[str, Any]:
        """
        Store all parsable info to `self.content` dict, when method fails,
        warning is raised

        :raises Warning: when race doesn't have an overview
        :return: `self.content` dict
        """
        try:
            race_year = self.race_year()
        except Exception:
            raise Warning("Couldn't find overview of the race")

        self.content = {
            "race_id": self.race_id(),
            "display_name": self.display_name(),
            "nationality": self.nationality(),
            "race_year": self.race_year(),
            "startdate": self.startdate(),
            "enddate": self.enddate(),
            "category": self.category(),
            "uci_tour": self.uci_tour(),
        }
        if not self.is_one_day_race():
            self.content['stages'] = self.stages()
        return self.content

    def display_name(self) -> str:
        """
        Parses display name from HTML

        :return: display name e.g. `Tour de France`
        """
        display_name_html = self.html.find(".page-title > .main > h1")[0]
        return display_name_html.text

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is one day race from HTML

        :return: whether given race is one day race
        """
        one_day_race_html = self.html.find("div.sub > span.blue")[0]
        return "stage" not in one_day_race_html.text.lower()

    def nationality(self) -> str:
        """
        Parses race nationality from HTML

        :return: 2 chars long country code
        """
        nationality_html = self.html.find(".page-title > .main > span")[0]
        return nationality_html.attrs['class'][1].upper()

    def race_year(self) -> int:
        """
        Parses race ridden year from HTML

        :return: race ridden year
        """
        race_year_html = self.html.find(".page-title > .main > font")[0]
        return int(race_year_html.text[:-2])

    def startdate(self) -> str:
        """
        Parses race startdate from HTML

        :return: startdate in `dd-mm-yyyy` format
        """
        startdate_html = self.html.find(".infolist > li > div:nth-child(2)")[0]
        return startdate_html.text

    def enddate(self) -> str:
        """
        Parses race enddate from HTML

        :return: enddate in `dd-mm-yyyy` format
        """
        enddate_html = self.html.find(".infolist > li > div:nth-child(2)")[1]
        return enddate_html.text

    def category(self) -> str:
        """
        Parses race category from HTML

        :return: race category e.g. `Men Elite`
        """
        category_html = self.html.find(".infolist > li > div:nth-child(2)")[2]
        return category_html.text

    def uci_tour(self) -> str:
        """
        Parses UCI Tour of the race from HTML

        :return: UCI Tour of the race e.g. `UCI Worldtour`
        """
        uci_tour_html = self.html.find(".infolist > li > div:nth-child(2)")[3]
        return uci_tour_html.text

    def stages(self, *args: str, available_fields: Tuple[str, ...] = (
            "date",
            "mtf",
            "course_type",
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
        stages_table_html = self.html.find("div:nth-child(3) > ul.list")[0]
        tp = TableParser(stages_table_html, "ul")
        tp.parse(fields, lambda x: True if "Restday" in x.text else False)
        tp.add_year_to_dates(self.year())
        return tp.table


class RaceStartlist(Race):
    def __init__(self, url: str, update_html: bool = True) -> None:
        """
        Creates RaceStartlist object ready for HTML parsing

        :param url: URL of race overview either full or relative, e.g.
        `race/tour-de-france/2021/startlist`
        :param update_html: whether to make request to given URL and update
        `self.html`, when False `self.update_html` method has to be called
        manually to make object ready for parsing, defaults to True
        """
        self._validate_url(url, "startlist")
        super().__init__(url, update_html)

    def parse_html(self) -> Dict[str, List]:
        """
        Store all parsable info to `self.content` dict

        :return: `self.content` dict
        """
        self.content = {
            "teams": self.teams(),
            "startlist": self.startlist()
        }
        return self.content

    def teams(self) -> List[str]:
        """
        Parses teams ids from HTML

        :return: list with team ids
        """
        teams_html = self.html.find("ul > li.team > b > a")
        return [team.attrs['href'].split("/")[1] for team in teams_html]

    def startlist(self) -> List[dict]:
        """
        Parses startlist from HTML

        :return: table with columns `rider_id`, `rider_number`, `team_id`
        represented as list of dicts
        """
        startlist = []
        teams_html = self.html.find("ul > li.team")
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
