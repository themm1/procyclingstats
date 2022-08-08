from datetime import date
from re import T
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from requests_html import HTML, Element
from tabulate import tabulate

from scraper import Scraper
from utils import add_time


def test():
    html = Scraper("race/tour-de-france/2022/stage-18", None, True).html
    categories = html.find(".result-cont > table > tbody")
    tp = TableParser(categories[0])
    tp.parse(["rank", "rider_url", "rider_name"])
    print(tabulate(tp.table))


class TableRowParser:
    """
    Parser for HTML table row, public methods parse data and return it

    :param row: table row (`tr` or `li` element currently) to be parsed from
    """
    row_child_tag_dict: Dict[str, str] = {
        "tr": "td",
        "li": "div"
    }
    """Finds out what is the row child tag based on table child tag"""

    def __init__(self, row: Element) -> None:
        self.row = row
        self.row_child_tag = self.row_child_tag_dict[row.tag]

    def _get_a(self, to_find: Literal["rider", "team", "race", "nation"],
               url: bool = False) -> str:
        """
        Gets `a` element and returns it's text or URL

        :param to_find: based on what keyword should be `a` element found
        :param url: whether to return URL, when False returns text, defaults to
        False
        :return: text of the element, if url is True href of the element
        """
        for a in self.row.find("a"):
            if a.attrs['href'].split("/")[0] == to_find:
                # return url of rider or team
                if url:
                    return a.attrs['href']
                # return name of rider or team
                else:
                    return a.text

    def rider_name(self) -> str:
        """
        Parses rider name

        :return: rider name e.g. `POGACAR Tadej`
        """
        return self._get_a("rider")

    def rider_url(self) -> str:
        """
        Parses rider URL from `a` element href

        :return: rider URL e.g. `rider/tadej-pogacar`
        """
        return self._get_a("rider", True)

    def team_name(self) -> str:
        """
        Parses team name

        :return: team name e.g. `BORA - hansgrohe`
        """
        return self._get_a("team")

    def team_url(self) -> str:
        """
        Parses team URL from `a` element href

        :return: team URL e.g. `team/bora-hansgrohe`
        """
        return self._get_a("team", True)

    def rank(self) -> Optional[int]:
        """
        Parses rank from table (first row column)

        :return: rank as int if found, otherwise None
        """
        rank_html = self.row.find(self.row_child_tag)[0]
        if not rank_html.text.isnumeric():
            return None
        else:
            return int(rank_html.text)

    def status(self) -> str:
        """
        Parses status (same element as rank)

        :return: if rank is numeric returns `DF` otherwise returns rank text
        value, e.g. `DNF`
        """
        status_html = self.row.find(self.row_child_tag)[0]
        if status_html.text.isnumeric():
            return "DF"
        else:
            return status_html.text

    def prev_rank(self) -> Union[int, None]:
        """
        Parses rank from previous stage (available only for stage races)

        :return: previous rank as int if found, otherwise None
        """
        rank_html = self.row.find(self.row_child_tag)[1]
        if rank_html.text:
            return int(rank_html.text)
        else:
            return None

    def age(self) -> int:
        """
        Parses age (available only for tables with riders)

        :return: age
        """
        age_html = self.row.find(self.row_child_tag)[0]
        return int(age_html.text)

    def nationality(self) -> str:
        """
        Parses nationality

        :return: nationality as 2 chars long country code in uppercase
        """
        nationality_html = self.row.find(".flag")[0]
        return nationality_html.attrs['class'][1].upper()

    def time(self) -> str:
        """
        Parses time

        :return: time, when first row is parsed absolute, otherwise relative
        """
        hidden_time_list = self.row.find(".time > .hide")
        if hidden_time_list:
            time = hidden_time_list[0].text
        else:
            time = self.row.find(".time")[0].text.split("\n")[0]
        if time == "-":
            time = None
        return time

    def bonus(self) -> int:
        """
        Parses bonus seconds gained (available only in stage races)

        :return: bonus seconds as int, 0 if not found
        """
        bonus_html_list = self.row.find(".bonis")
        if not bonus_html_list:
            return 0
        bonus = bonus_html_list[0].text.replace("″", "")
        if not bonus:
            return 0
        return int(bonus)

    def points(self) -> float:
        """
        Parses points (last `td` element from row that is not .delta_pnt)

        :return: points
        """
        points_html = self.row.find(f"{self.row_child_tag}:not(.delta_pnt)"
                                    ":not(.clear)")[-1]
        return float(points_html.text)

    def pcs_points(self) -> int:
        """
        Parses PCS points

        :return: PCS points, when not found returns 0
        """
        tds = self.row.find(self.row_child_tag)
        count = 0
        # get PCS points by getting eigth column that is not of class fs10
        for td in tds:
            if "class" not in td.attrs.keys() or\
                    "fs10" not in td.attrs['class'] and\
                    "gc" not in td.attrs['class']:
                count += 1
            if count == 8:
                pcs_points = td.text
                if pcs_points.isnumeric():
                    return int(pcs_points)
                else:
                    return 0

    def uci_points(self) -> float:
        """
        Parses UCI points

        :return: UCI points, when not found returns 0
        """
        tds = self.row.find(self.row_child_tag)
        # get UCI points by getting seventh column that is not of class fs10
        count = 0
        for td in tds:
            if "class" not in td.attrs.keys() or\
                    "fs10" not in td.attrs['class'] and\
                    "gc" not in td.attrs['class']:
                count += 1
            if count == 7:
                uci_points = td.text
                if uci_points.isnumeric():
                    return float(uci_points)
                else:
                    return 0

    def race_name(self) -> str:
        """
        Parses race name

        :return: race name e.g `Tour de France`
        """
        return self._get_a("race", False)

    def race_url(self) -> str:
        """
        Parses race URL from `a` element href

        :return: race's URL e.g. `race/tour-de-france`
        """
        return self._get_a("race", True)

    def nation_name(self) -> str:
        """
        Parses nation name

        :return: nation name e.g. `Belgium`
        """
        return self._get_a("nation", False)

    def nation_url(self) -> str:
        """
        Parses nation URL from `a` element href

        :return: nation url e.g. `nation/belgium`
        """
        return self._get_a("nation", True)

    def date(self) -> str:
        """
        Parses date with day and month (works only when date is in first column)

        :return: day and month separated by `-` e.g. `30-7`
        """
        raw_date = self.row.find(self.row_child_tag)[0].text
        return raw_date.replace("/", "-")

    def profile_icon(self) -> Literal["p0", "p1", "p2", "p3", "p4", "p5"]:
        """
        Parses profile icon

        :return: profile icon e.g. `p4`, the higher the number is the more
        difficult the profile is
        """
        return self.row.find(".icon.profile")[0].attrs['class'][-1]

    def stage_name(self) -> str:
        """
        Parses stage name from `a` element text

        :return: stage name e.g. `Stage 1 (ITT) | Copenhagen - Copenhagen`
        """
        return self._get_a("race")

    def stage_url(self) -> str:
        """
        Parses stage URL from `a` element href

        :return: stage URL e.g. `race/tour-de-france/2022/stage-1`
        """
        return self._get_a("race", True)

    def distance(self) -> float:
        """
        Parses distance of the stage (works only on race stages table)

        :return: distance in kms
        """
        distance_raw = self.row.find(self.row_child_tag)[-2].text
        # convert distance in `(12.2k)` format to 12.2 format
        return float(distance_raw.replace("k", "")[1:-1])

    def season(self) -> int:
        """
        Parses season (used for parsing tables from rider page)

        :return: season
        """
        return int(self.row.find(f"{self.row_child_tag}.season")[0].text)

    def rider_number(self) -> int:
        """
        Parses rider number (available in startlist_v3 only)

        :return: rider number
        """
        return int(self.row.text.split(" ")[0])

    def get_other(self, index: int) -> str:
        """
        Parses `td` elementh that is index-th child of current row HTML, used
        for elements that can't be accessed always by same path e.g. UCI points

        :param index: index of wanted `td` element, negative indexing works too
        :return: text attribute of wanted element
        """
        return self.row.find(self.row_child_tag)[index].text


class TableParser:
    """
    Parser for HTML tables, parsed content is stored in `self.table`, which is
    represented as list of dicts

    :param html_table: HTML table to be parsed from
    """

    child_tag_dict: Dict[str, Any] = {
        "tbody": "tr",
        "ul": "li"
    }
    """Finds out what is the table children tag"""
    ttt_fields: List[str] = [
        "rank",
        "time",
        "rider_name",
        "rider_url",
        "team_name",
        "team_url",
        "pcs_points",
        "uci_points",
        "pcs_points",
        "status"
    ]
    """Fields that are available in TTT results table"""

    def __init__(self, html_table: Element) -> None:
        self.html_table: HTML = html_table
        self.table_child_tag = self.child_tag_dict[html_table.tag]
        self.table: List[dict] = []

    def parse(self, fields: Union[List[str], Tuple[str, ...]],
              skip_when: callable = lambda _: False) -> None:
        """
        Parses HTML table to `self.table` (list of dicts) by calling given
        `TableRowParses` methods. Every parsed table row is dictionary with
        `fields` keys

        :param fields: `TableRowParser` public methods with no parameters to be
        called
        :param skip_when: function to call on every table row HTML, when returns
        True parser skips the row, always returns False by default
        :current fields options:
            - rider_name
            - rider_url
            - team_name
            - team_url
            - rank
            - status
            - prev_rank
            - age
            - nationality
            - time
            - bonus
            - points
            - pcs_points
            - uci_points
            - race_name
            - race_url
            - nation_name
            - nation_url
            - date
            - profile_icon
            - stage_name
            - stage_url
            - distance
            - season
        """
        for child_html in self.html_table.find(self.table_child_tag):
            if skip_when(child_html):
                continue
            row_parser = TableRowParser(child_html)
            # add to every wanted property to parsed table row by calling
            # corresponding method
            parsed_row = {field: getattr(row_parser, field)()
                          for field in fields}
            self.table.append(parsed_row)

    def parse_ttt_table(self, fields: List[str]) -> None:
        """
        Special method for parsing TTT results

        :param fields: wanted fields (public `TableParser` methods are current\
            options)
        :return: table with wanted fields represented as list of dicts
        """
        for tr in self.html_table.find(self.table_child_tag):
            trp = TableRowParser(tr)
            if "team" in tr.attrs['class']:
                current_rank = trp.rank()
                # gets third td element, which is time
                current_team_time = trp.get_other(2)
                current_team_name = trp.team_name()
                current_team_url = trp.team_url()
            else:
                rider_name = trp.rider_name()
                rider_url = trp.rider_url()
                extra_time = tr.find("span.blue")
                pcs_points = tr.find(".ac")[0].text
                pcs_points = 0 if not pcs_points else int(pcs_points)
                uci_points = tr.find(".ac.blue")[0].text
                uci_points = 0 if not uci_points else float(uci_points)
                if extra_time:
                    rider_time = add_time(extra_time[0].text, current_team_time)
                else:
                    rider_time = add_time(current_team_time, "00:00:00")
                full_dict = {
                    "rank": current_rank,
                    "time": rider_time,
                    "rider_name": rider_name,
                    "rider_url": rider_url,
                    "team_name": current_team_name,
                    "team_url": current_team_url,
                    "pcs_points": pcs_points,
                    "uci_points": uci_points,
                    "status": "DF"
                }
                self.table.append({})
                # drop unwanted fields
                for field in full_dict.keys():
                    if field in fields:
                        self.table[-1][field] = full_dict[field]

    def extend_table(self, field_name: str, index: int, func: callable) -> None:
        """
        Extends table by adding text of index-th `td` element from each row from
        HTML table

        :param field_name: key that will represent parsed value in table row
        dict
        :param index: index of `tr` child element that will be parsed
        :param func: function to be called on parsed string
        """
        for i, child_html in enumerate(
                self.html_table.find(self.table_child_tag)):
            row_parser = TableRowParser(child_html)
            if i >= len(self.table):
                self.table.append(
                    {field_name: func(row_parser.get_other(index))}
                )
            else:
                self.table[i][field_name] = func(row_parser.get_other(index))

    def make_times_absolute(self, time_field: str = "time") -> None:
        """
        Sums all times from table with first time from table. Table has to have
        at least 2 rows.

        :param time_field: field which represents wanted time, defaults to
        `time`
        """
        first_time = self.table[0][time_field]
        self.table[0][time_field] = add_time(first_time, "00:00:00")
        for row in self.table[1:]:
            if row[time_field]:
                row[time_field] = add_time(first_time, row['time'])

    def add_year_to_dates(self, year: int, date_field: str = "date") -> None:
        """
        Adds year to dates in table, used when parsing table with stages from
        race overview where dates are in `30-7` format

        :param year: year to add to dates
        :param date_field: field which represents wanted date, defaults to
        `date`
        """
        for row in self.table:
            if row[date_field]:
                row[date_field] = f"{row[date_field]}-{str(year)}"

    def table_to_dict(self, key_field: str) -> Dict[str, dict]:
        """
        Converts table to dictionary with given key

        :param key_field: table row field which value is unique for each row
        e.g. `rider_url`, key has to be in every table row
        :raises ValueError: when `key_field` is not in table row
        :return: dictionary where given table field values are keys and rows of
        original table are values
        """
        try:
            return {row[key_field]: row for row in self.table}
        except KeyError:
            raise ValueError(f"Invalid key_field argument: {key_field}")


if __name__ == "__main__":
    test()
