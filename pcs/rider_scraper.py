import calendar
from pprint import pprint
from typing import Any, Dict, List, Tuple

from tabulate import tabulate

from parsers import TableParser
from scraper import Scraper
from utils import get_day_month, parse_table_fields_args


def test():
    # rider = Rider("rider/david-canada")
    rider = Rider("rider/peter-sagan")
    # rider = Rider("rider/cesare-benedetti")
    # rider = Rider("rider/carlos-verona")
    table = rider.seasons_points("position")
    print(tabulate(table))


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

    def seasons_teams(self, *args: Tuple[str], available_fields: Tuple[str] = (
        "season", "since", "until", "team_name", "team_url", "class"
    )) -> List[dict]:
        """
        Parses rider's teams per season from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        seasons_html_table = self.html.find("ul.list.rdr-teams")[0]
        tp = TableParser(seasons_html_table, "ul")
        casual_fields = [field for field in fields if field == "team_name" or
                         field == "team_url"]
        if "since" in fields or "until" in fields or "season" in fields:
            casual_fields.append("season")
        tp.parse(casual_fields)
        # add class and convert it from `(WT)` to `WT`
        if "class" in fields:
            tp.extend_table("class", -3,
                            lambda x: x.replace("(", "").replace(")", ""))
        # add since and until dates to the table
        if "since" in fields or "until" in fields:
            tp.extend_table("since_until", -2, str)
            for row in tp.table:
                if "since" in fields:
                    # add as from to since date
                    if "as from" in row['since_until']:
                        day, month = get_day_month(row['since_until'])
                        row['since'] = f"{day}-{month}-{row['season']}"
                    else:
                        row['since'] = f"01-01-{row['season']}"
                if "until" in fields:
                    # add until to until date
                    if "until" in row['since_until']:
                        day, month = get_day_month(row['since_until'])
                        row['until'] = f"{day}-{month}-{row['season']}"
                    else:
                        row['until'] = f"31-12-{row['season']}"
                # remove unnecessary fields
                if "season" not in fields:
                    row.pop("season")
                row.pop("since_until")
        return tp.table

    def seasons_points(self, *args: Tuple[str], available_fields: Tuple[str] = (
            "season", "points", "position")) -> List[dict]:
        """
        Parses rider's points per season from HTML

        :param *args: fields that should be contained in table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        points_table_html = self.html.find(".rdr-season-stats > tbody")[0]
        tp = TableParser(points_table_html)

        tp.parse(["season"])
        if "points" in fields:
            tp.extend_table("points", -2, int)
        if "position" in fields:
            tp.extend_table("position", -1, int)
        if "season" not in fields:
            for row in tp.table:
                row.pop("season")
        return tp.table


if __name__ == "__main__":
    test()
