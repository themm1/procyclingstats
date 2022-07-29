from typing import List, Literal, Tuple, Union

from requests_html import HTML

from utils import add_time


class TableParser:
    def __init__(self, html_table: HTML, table: Union[list, None] = None):
        """
        Parsed content is stored in `self.table`, which is represented as list\
            of dicts

        :param html_table: HTML table to be parsed from
        :param table: table to be parsed to, if None new one is created,\
            defaults to None
        """
        self.html_table: HTML = html_table
        self.table: List[dict] = []
        if table:
            self.table = table

    def parse(self, fields: List[str]) -> None:
        """
        Parses HTML table to `self.table` (list of dicts) by calling given \
            `TableRowParses` methods. Every parsed table row is dictionary with\
            `fields` keys

        :param fields: `TableRowParser` methods to be called, current options:
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
        """
        for tr_html in self.html_table.find("tr"):
            tr = TableRowParser(tr_html)
            # add to every wanted property to parsed table row by calling
            # corresponding method
            parsed_row = {field: getattr(tr, field)() for field in fields}
            self.table.append(parsed_row)

    def extend_table(self, field_name: str, index: int, func: callable) -> None:
        """
        Extends table by adding text of index-th `td` element from each row\
            from HTML table

        :param field_name: key that will represent parsed value in table row\
            dict
        :param index: index of `tr` child element that will be parsed
        :param func: function to be called on parsed string
        """
        for i, tr_html in enumerate(self.html_table.find("tr")):
            tr = TableRowParser(tr_html)
            self.table[i][field_name] = func(tr.get_other(index))

        # if extra_table:

    def make_times_absolute(self) -> None:
        """
        Sums all times from table with first time from table. Time fields are\
            required to be called `time` and table has to have at least 2 rows.
        """
        first_time = self.table[0]['time']
        self.table[0]['time'] = add_time(first_time, "00:00:00")
        for row in self.table[1:]:
            if row['time']:
                row['time'] = add_time(first_time, row['time'])


def parse_ttt_table(html_table: HTML, fields: List[str],
                    extra_table: Union[HTML, None] = None) -> List[dict]:
    """
    Special function for parsing TTT results

    :param html_table: TTT results HTML table to be parsed from
    :param fields: wanted fields (public `TableParser` methods are current\
        options)
    :param extra_table: extra HTML table from which fields like age or\
        nationality will be parsed, defaults to None
    :return: table with wanted fields represented as list of dicts
    """
    ttt_table = {}

    for tr in html_table:
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
            pcs_points = tr.find(".ac")[0]
            pcs_points = 0 if not pcs_points else int(pcs_points)
            uci_points = tr.find(".ac.blue")[0]
            uci_points = 0 if not uci_points else float(uci_points)
            if extra_time:
                rider_time = add_time(extra_time[0].text, current_team_time)
            else:
                rider_time = current_team_name
            ttt_table[rider_url] = {
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
            # drop unwanted fields
            for field in fields:
                if field in ttt_table[rider_url].keys():
                    ttt_table[rider_url].pop(field)
    # add more fields to table if needed and extra table is available
    if extra_table:
        ttt_fields = [
            "rank", "time", "rider_name", "rider_url", "team_name", "team_url",
            "pcs_points", "uci_points", "pcs_points", "status"
        ]
        tp = TableParser(extra_table)
        # remove fields that are already set
        fields = [field for field in fields if field not in ttt_fields]
        tp.parse(fields.append("rider_url"))
        new_table = []
        for row in tp.table:
            ttt_table_row = ttt_table[row['rider_url']]
            # merge tables together
            new_table.append({**row, **ttt_table_row})
        return new_table
    return ttt_table


class TableRowParser:
    def __init__(self, tr: HTML) -> None:
        """
        Parses row of a table

        :param tr: table row (`tr` element) to be parsed from
        """
        self.tr = tr

    def _get_a(self, to_find: Literal["rider", "team", "race"],
               url: bool = False) -> str:
        """
        Gets `a` element and returns it's text or URL

        :param to_find: whether to find team, rider or race `a` element
        :param url: whether to return URL, when False returns text, defaults to\
            False
        :return: URL or name of team, rider or race
        """
        for a in self.tr.find("a"):
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

    def rank(self) -> Union[int, None]:
        """
        Parses rank from table (first row column)

        :return: rank as int if found, otherwise None
        """
        rank_html = self.tr.find("td")[0]
        if not rank_html.text.isnumeric():
            return None
        else:
            return int(rank_html.text)

    def status(self) -> str:
        """
        Parses status (same element as rank)

        :return: if rank is numeric returns `DF` otherwise returns rank text\
            value, e.g. `DNF`
        """
        status_html = self.tr.find("td")[0]
        if status_html.text.isnumeric():
            return "DF"
        else:
            return status_html.text

    def prev_rank(self) -> Union[int, None]:
        """
        Parses rank from previous stage (available only for stage races)

        :return: previous rank as int if found, otherwise None
        """
        rank_html = self.tr.find("td")[1]
        if rank_html.text:
            return int(rank_html.text)
        else:
            return None

    def age(self) -> int:
        """
        Parses age (available only for tables with riders)

        :return: age
        """
        age_html = self.tr.find(".age")[0]
        return int(age_html.text)

    def nationality(self) -> str:
        """
        Parses nationality

        :return: nationality as 2 chars long country code in uppercase
        """
        nationality_html = self.tr.find(".flag")[0]
        return nationality_html.attrs['class'][1].upper()

    def time(self) -> str:
        """
        Parses time

        :return: time, when first row is parsed absolute, otherwise relative
        """
        hidden_time_list = self.tr.find(".time > .hide")
        if hidden_time_list:
            time = hidden_time_list[0].text
        else:
            time = self.tr.find(".time")[0].text.split("\n")[0]
        if time == "-":
            time = None
        return time

    def bonus(self) -> int:
        """
        Parses bonus seconds gained (available only in stage races)

        :return: bonus seconds as int, 0 if not found
        """
        bonus_html_list = self.tr.find(".bonis")
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
        points_html = self.tr.find("td:not(.delta_pnt)")[-1]
        return float(points_html.text)

    def pcs_points(self) -> int:
        """
        Parses PCS points

        :return: PCS points, when not found returns 0
        """
        tds = self.tr.find("td")
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
        tds = self.tr.find("td")
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
        return self._get_a("race", False)

    def race_url(self) -> str:
        return self._get_a("race", True)

    def get_other(self, index: int) -> str:
        """
        Parses `td` elementh that is index-th child of current row HTML, used\
            for elements that can't be accessed always by same path e.g. UCI\
            points

        :param index: index of wanted `td` element
        :return: text attribute of wanted element
        """
        return self.tr.find("td")[index].text
