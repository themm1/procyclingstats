from pprint import pprint
from typing import Dict, List, Tuple

from tabulate import tabulate

from scraper import Scraper
from utils import get_day_month


def test():
    t = Team("team/quickstep-innergetic-2010")
    print(t.abbreviation())
    print(t.bike())
    print(t.display_name())
    print(t.team_id())
    print(t.season())
    print(t.team_status())
    print(t.team_ranking_position())
    print(t.wins_count())
    pprint(t.urls())
    # print(tabulate(t.riders()))


class Team(Scraper):
    def __init__(self, team_url: str, print_request_url: bool = False) -> None:
        """
        Creates Team object ready for HTML parsing

        :param team_url: team URL, either full or relative, e.g. 
        `team/bora-hansgrohe-2022`
        :param print_request_url: whether to print URL when making request,
        defaults to False
        """
        super().__init__(team_url, print_request_url)
        self.content = {}

    def urls(self) -> List[str]:
        """
        Parses URLs of the team from past and future seasons

        :return: list with realtive team URLs
        """
        team_seasons_elements = self.html.find("form > select > option")
        urls = []
        for element in team_seasons_elements:
            url = element.attrs['value']
            # remove /overview/ if needed
            if "overview" in url:
                urls.append("/".join(url.split("/")[:-2]))
        return urls

    def riders(self) -> List[dict]:
        """
        Parses riders from team during season from HTML

        :return: table with columns `rider_id`, `nationality, `since`, `until`,
            `career_points`, `age` represented as list of dicts
        """
        year = self.season()
        path = ".ttabs.tabb:not(.hide) > ul > li"
        nationalities_elements = self.html.find(
            f"{path} > div:nth-child(2) > span")
        rider_ids_elemetns = self.html.find(f"{path} > div:nth-child(2) > a")
        since_elements = self.html.find(f"{path} > div:nth-child(3)")

        # dict is used because of extending table with age or career points
        # afterwards
        season_riders = {}
        for i, rider_element in enumerate(rider_ids_elemetns):
            since_until_str = since_elements[i].text

            since_day, since_month = "01", "01"
            if "as from" in since_until_str:
                since_day, since_month = get_day_month(since_until_str)
            until_day, until_month = "31", "12"
            if "until" in since_until_str:
                until_day, until_month = get_day_month(since_until_str)

            rider_id = rider_element.attrs['href'].split("/")[1]
            nationality = nationalities_elements[i].attrs['class'][1].upper()
            season_riders[rider_id] = {
                "rider_id": rider_id,
                "nationality": nationality,
                "since": f"{since_day}-{since_month}-{year}",
                "until": f"{until_day}-{until_month}-{year}",
            }
        self._add_career_points_to_table(season_riders)
        self._add_ages_to_table(season_riders)
        return list(season_riders.values())

    def _add_career_points_to_table(self, table: Dict[str, dict]) -> None:
        """
        Parses career points of each rider from HTML and adds points to given
        table, note that career points are rider's current career points,
        not career points in corresponding season

        :param table: table to be extended represented as dict of dicts where
        key should be rider id
        """
        riders_ids_htmls = self.html.find(
            ".taba > ul > li > div:nth-child(2) > a")
        career_points_htmls = self.html.find(
            ".taba > ul > li > div:nth-child(3)")

        zipped_htmls = zip(riders_ids_htmls, career_points_htmls)
        for rider_id_html, career_points_html in zipped_htmls:
            rider_id = rider_id_html.attrs['href'].split("/")[1]
            career_points = int(career_points_html.text)
            table[rider_id]['career_points'] = career_points

    def _add_ages_to_table(self, table: Dict[str, dict]) -> None:
        """
        Parses age of each rider from HTML and adds age to given table, in
        historical seasons age is taken from July 1st

        :param table: table to be extended represented as dict of dicts where
        key should be rider id
        """
        riders_ids_htmls = self.html.find(
            ".tabc > ul > li > div:nth-child(2) > a")
        age_htmls = self.html.find(
            ".tabc > ul > li > div:nth-child(3)")

        zipped_htmls = zip(riders_ids_htmls, age_htmls)
        for rider_id_html, age_html in zipped_htmls:
            rider_id = rider_id_html.attrs['href'].split("/")[1]
            age = int(age_html.text)
            table[rider_id]['age'] = age

    def team_id(self) -> str:
        """
        Parses team id from URL, season is part of team id

        :return: team id e.g. `bora-hansgrohe-2022`
        """
        return self._cut_base_url().split("/")[1]

    def season(self) -> int:
        """
        Parses season from URL

        :return: season
        """
        team_id = self._cut_base_url().split("/")[1]
        season_part = team_id.split("-")[-1]
        # only first 4 characters are used because some teams might have fifth
        # character, which isn't part of season e.g. movistar-team-20152
        return int(season_part[:4])

    def display_name(self) -> str:
        """
        Parses team display name from HTML

        :return: display name e.g. `BORA - hansgrohe`
        """
        display_name_html = self.html.find(".page-title > .main > h1")[0]
        return display_name_html.text.split(" (")[0]

    def nationality(self) -> str:
        """
        Parses team's nationality from HTML

        :return: team's nationality as 2 chars long country code in uppercase
        """
        nationality_html = self.html.find(".page-title > .main > span.flag")[0]
        return nationality_html.attrs['class'][1].upper()

    def team_status(self) -> str:
        """
        Parses team status from HTML

        :return: team status as 2 chars long code in uppercase e.g. `WT` (World
        Tour)
        """
        team_status_html = self.html.find(
            "div > ul.infolist > li:nth-child(1) > div")[1]
        return team_status_html.text

    def abbreviation(self) -> str:
        """
        Parses team abbreviation from HTML

        :return: team abbreviation as 3 chars long code in uppercase e.g. `BOH`
        (BORA - hansgrohe)
        """
        abbreviation_html = self.html.find(
            "div > ul.infolist > li:nth-child(2) > div")[1]
        return abbreviation_html.text

    def bike(self) -> str:
        """
        Parses team's bike brand from HTML

        :return: bike brand e.g. `Specialized`
        """
        bike_html = self.html.find(
            "div > ul.infolist > li:nth-child(3) > div")[1]
        return bike_html.text

    def wins_count(self) -> int:
        """
        Parses count of wins in corresponding season from HTML

        :return: count of wins in corresponding season
        """
        team_ranking_html = self.html.find(
            ".teamkpi > li:nth-child(1) > div:nth-child(2)")[0]
        return int(team_ranking_html.text)

    def team_ranking_position(self) -> int:
        """
        Parses team ranking position from HTML

        :return: PCS team ranking position in corresponding year
        """
        team_ranking_html = self.html.find(
            ".teamkpi > li:nth-child(2) > div:nth-child(2)")[0]
        return int(team_ranking_html.text)


if __name__ == "__main__":
    test()
