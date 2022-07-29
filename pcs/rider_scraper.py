import calendar
import datetime
from pprint import pprint
from typing import Any, Dict, List

from scraper import Scraper


def test():
    # rider = Rider("rider/david-canada")
    # rider = Rider("rider/peter-sagan")
    rider = Rider("rider/cesare-benedetti")
    rider_response = rider.parse_html()
    pprint(rider_response)


class Rider(Scraper):
    def __init__(self, rider_url: str, print_request_url: bool = False) -> None:
        """
        Creates rider object ready for HTML parsing

        :param rider_url: rider's URL either full or relative, e.g.
        `rider/tadej-pogacar`
        :param print_request_url: whether to print URL when making request,
        defaults to False
        """
        super().__init__(rider_url, print_request_url)
        self.content = {}

    def parse_html(self) -> Dict[str, Any]:
        """
        Stores all parsable info to `self.content` dict

        :return: `self.content` dict
        """
        self.content['info'] = {
            "rider_id": self.url.split("/")[-1],
            "name": self.name(),
            "weight": self.weight(),
            "height": self.height(),
            "birthdate": self.birthdate(),
            "nationality": self.nationality(),
            "place_of_birth": self.place_of_birth(),
        }
        self.content['teams_seasons'] = self.seasons_teams()
        self.content['points_season'] = self.seasons_points()
        return self.content

    def birthdate(self) -> str:
        """
        Parses rider's birthdate from HTML

        :return: birthday of the rider in `yyyy-mm-dd` format
        """
        general_info = self.html.find(".rdr-info-cont")[0].text.split("\n")
        birth_string = general_info[0].split(": ")[1]
        [date, month, year] = birth_string.split(" ")[:3]
        date = "".join([char for char in date if char.isnumeric()])
        month = list(calendar.month_name).index(month)
        return "-".join([str(year), str(month), date])

    def place_of_birth(self) -> str:
        """
        Parses rider's place of birth from HTML

        :return: rider's place of birth (town only)
        """
        # normal layout
        try:
            place_of_birth_html = self.html.find(
                ".rdr-info-cont > span > span > a")[0]
            return place_of_birth_html.text
        # special layout
        except IndexError:
            place_of_birth_html = self.html.find(
                ".rdr-info-cont > span > span > span > a")[0]
            return place_of_birth_html.text

    def name(self) -> str:
        """
        Parses rider's name from HTML

        :return: rider's name
        """
        return self.html.find(".page-title > .main > h1")[0].text

    def weight(self) -> int:
        """
        Parses rider's current weight from HTML

        :return: rider's weigth
        """
        # normal layout
        try:
            return int(self.html.find(".rdr-info-cont > span")
                       [1].text.split(" ")[1])
        # special layout
        except IndexError:
            return int(self.html.find(".rdr-info-cont > span > span")
                       [1].text.split(" ")[1])

    def height(self) -> float:
        """
        Parses rider's height from HTML

        :return: rider's height
        """
        # normal layout
        try:
            height_html = self.html.find(".rdr-info-cont > span > span")[0]
            return float(height_html.text.split(" ")[1])
        # special layout
        except IndexError:
            height_html = self.html.find(
                ".rdr-info-cont > span > span > span")[0]
            return float(height_html.text.split(" ")[1])

    def nationality(self) -> str:
        """
        Parses rider's nationality from HTML

        :return: rider's current nationality as 2 chars long country code in
        uppercase
        """
        # normal layout
        try:
            nationality_html = self.html.find(".rdr-info-cont > span")[0]
            return nationality_html.attrs['class'][1].upper()
        # special layout
        except KeyError:
            nationality_html = self.html.find(
                ".rdr-info-cont > span > span")[0]
            return nationality_html.attrs['class'][1].upper()

    def seasons_teams(self) -> List[dict]:
        """
        Parses rider's team history with the exact date of joining from HTML

        :return: table with columns `team_season_id`, `since` represented as
        list of dicts
        """
        teams_html = self.html.find(".rdr-teams > li > .name > a")
        years_html = self.html.find(".rdr-teams > li > .season")
        dates_html = self.html.find(".rdr-teams > li > .fs10")

        current_year = datetime.datetime.now().year

        # extract information from html elements
        years = [int(element.text)
                 for element in years_html if int(element.text) <= current_year]
        seasons_count = len(years_html)
        teams = [element.attrs['href'].split("/")[1]
                 for element in teams_html[-seasons_count+1:]]
        dates = [element.text for element in dates_html[-seasons_count+1:]]

        seasons = []
        for i, team in enumerate(teams):
            year = years[i]
            date = dates[i]

            # rider transfered during the year
            if "as from" in date:
                transfer = date.split(" ")
                date = [t_date
                        for t_date in transfer if t_date[0].isnumeric()][0]
                [day, month] = date.split("/")
                since = "-".join([str(year), month, day])
            # rider has been in the team since the beginning of the year
            else:
                since = f"{year}-01-01"

            seasons.append({
                "team_season_id": team,
                "since": since,
            })
        return seasons

    def seasons_points(self) -> List[dict]:
        """
        Parses rider's PCS ranking points and position in each season from HTML

        :return: table with columns `season`, `points`, `position` represented 
        as list of dicts
        """
        seasons_html = self.html.find(
            ".rdr-season-stats > tbody > tr > td.season")
        points_html = self.html.find(
            ".rdr-season-stats > tbody > tr > td > div > span")
        positions_html = self.html.find(
            ".rdr-season-stats > tbody > tr > td:nth-child(3)")

        zipped_htmls = zip(seasons_html, points_html, positions_html)
        # convert list of tuples to list of dicts
        seasons_points = []
        for season, points, pos in zipped_htmls:
            seasons_points.append({
                "season": int(season.text),
                "points": int(points.text),
                "position": int(pos.text)
            })
        return seasons_points


if __name__ == "__main__":
    test()
