from pprint import pprint
from typing import List, Dict, Any, Literal
from requests_html import HTML
from tabulate import tabulate

from utils import RequestWrapper


def test():
    # RaceOverview()
    url = "race/tour-de-france/2022"
    race = RaceOverview(url)
    race.update_html()
    race.parse_html()
    pprint(race.content)

    # stages = RaceStages(url)
    # stages.update_html()
    # stages.parse_html()
    # pprint(stages.content)

    # startlist = RaceStartlist(url)
    # startlist.update_html()
    # startlist.parse_html()
    # pprint(startlist.teams())


class Race(RequestWrapper):
    """
    General Race class

    Attributes:
        url: URL of the race, e.g. `race/tour-de-france/2021`
        print_request_url: whether to print URL of request when making request
        html: HTML from the URL, empty on default, call `self.update_html` to\
            update
        content: dict with parsed information, call `self.parse_html` to update

    Args:
        race_url: URL of the race, e.g. `race/tour-de-france/2021`
        print_request_url: whether to print URL of request when making request

    see base class for other inhereted attributes
    """
    def __init__(self, race_url: str, print_request_url: bool=True) -> None:
        super().__init__(race_url, print_request_url)
        
    @staticmethod
    def _validate_url(url: str, original_url: str, extra: \
        Literal["", "overview", "startlist"]="", stage: bool=False) -> None:
        """
        Checks whether given URL is valid, is used by `Stage` class too
        :param url: race URL to be validate e.g. `race/tour-de-france/2021`
        :param original_url: unformatted URL that was given while constructing\
            race object
        :param extra: string that should URL contain after regular race URL\
            e.g. `overview`
        :param stage: whether given URL is stage URL
        :raises: `ValueError` when URL is invalid
        """
        url_to_check = [element for element in url.split("/") if element != ""]
        try:
            # remove self.base_url from URL if needed
            if "https" in url:
                url_to_check = url_to_check[3:] 
            length = 4 if extra or stage else 3
            # check criteria of valid URL
            valid = len(url_to_check) == length and \
                url_to_check[0] == "race" and \
                url_to_check[2].isnumeric() and \
                len(url_to_check[2]) == 4
            if extra and valid:
                valid = url_to_check[3] == extra
            if not valid:
                raise ValueError(f"Invalid URL: {original_url}")
        # if criteria couldn't been checked URL is invalid
        except IndexError:
            raise ValueError(f"Invalid URL: {original_url}")

    @staticmethod
    def _format_url(url: str, extra: str) -> str:
        """
        :param url: URL to format
        :param extra: extra part to add to URL
        :returns: formatted URL and extra part added together
        """
        formatted_url = url
        if extra not in url and url[-1] == "/":
            formatted_url += extra
        elif extra not in url:
            formatted_url += "/" + extra
        return formatted_url

    def race_id(self) -> str:
        """:returns: race id parsed from URL e.g. `tour-de-france`"""
        return self.url.split("/")[1]
    
    def year(self) -> int:
        """:returns: year when the race occurred parsed from URL"""
        return int(self.url.split("/")[2])
    
    def race_season_id(self) -> str:
        """:returns: race seson id parsed from URL e.g. `tour-de-france/2021`"""
        return self.url.split("/")[1:3]


class RaceOverview(Race):
    """
    Parses overview from race overview page
    
    Attributes:
        url: URL of the race, e.g. `race/tour-de-france/2021`
        print_request_url: whether to print URL of request when making request
        html: HTML from the URL, empty on default, call `self.update_html` to\
            update
        content: dict with parsed information, call `self.parse_html` to update
    Args:
        race_url: URL of race, e.g. `race/tour-de-france/2021`, `/overview` can
            be omitted
        print_request_url: whether to print URL of request when making request
    see base class for more inhereted attributes
    """
    def __init__(self, race_url: str, print_request_url: bool=True) -> None:
        formatted_url = self._format_url(race_url, "overview")
        self._validate_url(formatted_url, race_url, "overview")
        super().__init__(formatted_url, print_request_url)
        
    def parse_html(self) -> Dict[str, Any]:
        """
        Store all parsable info to `self.content` dict, when method fails,\
            warning is raised
        :returns: `self.content` dict
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
        return self.content

    def display_name(self) -> str:
        """:returns: race display name"""
        display_name_html = self.html.find(".page-title > .main > h1")[0]
        return display_name_html.text

    def nationality(self) -> str:
        """:returns: race nationality as 2 chars long code in uppercase"""
        nationality_html = self.html.find(".page-title > .main > span")[0]
        return nationality_html.attrs['class'][1].upper()

    def race_year(self) -> int:
        """:returns: ridden season of the race"""
        race_year_html = self.html.find(".page-title > .main > font")[0]
        return int(race_year_html.text[:-2])

    def startdate(self) -> str:
        """:returns: date when the race starts as `yyyy-mm-dd`"""
        startdate_html = self.html.find(".infolist > li > div:nth-child(2)")[0]
        return startdate_html.text

    def enddate(self) -> str:
        """:returns: date when the race ends as `yyyy-mm-dd`"""
        enddate_html = self.html.find(".infolist > li > div:nth-child(2)")[1]
        return enddate_html.text

    def category(self) -> str:
        """:returns: race category e.g. `Men Elite`"""
        category_html = self.html.find(".infolist > li > div:nth-child(2)")[2]
        return category_html.text

    def uci_tour(self) -> str:
        """:returns: UCI Tour of the race e.g. `UCI Worldtour`"""
        uci_tour_html = self.html.find(".infolist > li > div:nth-child(2)")[3]
        return uci_tour_html.text


class RaceStages(Race):
    """
    Parses stages of a race

    Attributes:
        url: URL of the race, e.g. `race/tour-de-france/2021`
        print_request_url: whether to print URL of request when making request
        html: HTML from the URL, empty on default, call `self.update_html` to\
            update
        content: dict with parsed information, call `self.parse_html` to update
    Args:
        race_url: URL of race, e.g. `race/tour-de-france/2021`
        print_request_url: whether to print URL of request when making request
    see base class for more inhereted attributes
    """
    def __init__(self, race_url: str, print_request_url: bool=True) -> None:
        self._validate_url(race_url, race_url)
        super().__init__(race_url, print_request_url)

    def parse_html(self) -> Dict[str, List[str]]:
        """
        Store all parsable info to `self.content` dict
        :returns: `self.content` dict
        """
        self.content['stages'] = self.stages()
        return self.content

    def stages(self) -> List[str]:
        """:returns: race stages urls, if one day race returns list with one\
            stage"""
        stages_html = self.html.find(f"div > .pageSelectNav > div > form > \
            select > option")
        stages = [element.attrs['value']
            for element in stages_html if "-" in element.text]
        # remove /result from all stages URLs
        stages = ["/".join(stage.split("/")[:4]) for stage in stages]
        if not stages:
            # is one day race
            stages = [self.url]
        else:
            # remove duplicates
            stages = list(dict.fromkeys(stages))
        return stages


class RaceStartlist(Race):
    """
    Parses riders and teams from the startlist of a race

    Attributes:
        url: URL of the race, e.g. `race/tour-de-france/2021`
        print_request_url: whether to print URL of request when making request
        html: HTML from the URL, empty on default, call `self.update_html` to\
            update
        content: dict with parsed information, call `self.parse_html` to update
    Args:
        race_url: URL of race, e.g. `race/tour-de-france/2021`, `/startlist`
            can be omitted
        print_request_url: whether to print URL of request when making request
    see base class for more inhereted attributes
    """
    def __init__(self, race_url: str, print_request_url: bool=True) -> None:
        formatted_url = self._format_url(race_url, "startlist")
        self._validate_url(formatted_url, race_url, "startlist")
        super().__init__(formatted_url, print_request_url)

    def parse_html(self) -> Dict[str, List]:
        """
        Store all parsable info to `self.content` dict
        :returns: `self.content` dict
        """
        self.content = {
            "teams": self.teams(),
            "startlist": self.startlist()
        }
        return self.content
    
    def teams(self) -> List[str]:
        """:returns: list with ids of teams from startlist"""
        teams_html = self.html.find("ul > li.team > b > a")
        return [team.attrs['href'].split("/")[1] for team in teams_html]

    def startlist(self) -> List[dict]:
        """
        Parses startlist to list of dicts 
        :returns: table with columns `rider_id`, `rider_number`, `team_id`\
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