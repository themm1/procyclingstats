from typing import Any, Dict, List, Literal, Optional

from selectolax.parser import HTMLParser, Node

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import (add_times, convert_date, format_time, join_tables,
                    parse_table_fields_args)


class Stage(Scraper):
    """
    Scraper for stage results HTML page.

    Usage:

    >>> from procyclingstats import Stage
    >>> stage = Stage("race/tour-de-france/2022/stage-18")
    >>> stage.date()
    '2022-07-21'
    >>> stage.parse()
    {
        'arrival': Hautacam
        'date': '2022-07-21'
        'departure': 'Lourdes'
        'distance': 143.2
        'gc': [
            {
                'age': 25,
                'bonus': 0:00:32,
                'nationality': 'DK',
                'pcs_points': 0,
                'prev_rank': 1,
                'rank': 1,
                'rider_name': 'VINGEGAARD Jonas',
                'rider_url': 'rider/jonas-vingegaard-rasmussen',
                'team_name': 'Jumbo-Visma',
                'team_url': 'team/team-jumbo-visma-2022',
                'time': '71:53:34',
                'uci_points': 25.0
            },
            ...
        ],
        ...
    }
    """
    _tables_path = ".result-cont table"

    def _set_up_html(self) -> None:
        """
        Overrides Scraper method. Modifies HTML if stage is TTT by adding team
        ranks to riders.
        """
        # add team ranks to every rider's first td element, so it's possible
        # to map teams to riders based on their rank
        categories = self.html.css(self._tables_path)
        if not categories:
            return
        results_table_html = categories[0]
        if self.stage_type() != "TTT":
            return
        current_rank_node = None
        for column in results_table_html.css("tr > td:first-child"):
            rank = column.text()
            if rank:
                current_rank_node = column
            elif current_rank_node:
                column.replace_with(current_rank_node) # type: ignore

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is an one day race from HTML.

        :return: Whether the race is an one day race.
        """
        # If there are elements with .restabs class (Stage/GC... menu), the race
        # is a stage race
        return len(self.html.css(".restabs")) == 0

    def distance(self) -> float:
        """
        Parses stage distance from HTML.

        :return: Stage distance in kms.
        """
        distance = self._stage_info_by_label("Distance")
        return float(distance.split(" km")[0])

    def profile_icon(self) -> Literal["p0", "p1", "p2", "p3", "p4", "p5"]:
        """
        Parses profile icon from HTML.

        :return: Profile icon e.g. ``p4``, the higher the number is the more
            difficult the profile is.
        """
        profile_html = self.html.css_first("span.icon")
        return profile_html.attributes['class'].split(" ")[2] # type: ignore

    def stage_type(self) -> Literal["ITT", "TTT", "RR"]:
        """
        Parses stage type from HTML.

        :return: Stage type, e.g. ``ITT``.
        """
        stage_name_html = self.html.css_first(".sub > .blue")
        stage_name2_html = self.html.css_first("div.main > h1")
        stage_name = stage_name_html.text()
        stage_name2 = stage_name2_html.text()
        if "ITT" in stage_name or "ITT" in stage_name2:
            return "ITT"
        if "TTT" in stage_name or "TTT" in stage_name2:
            return "TTT"
        return "RR"

    def winning_attack_length(self):
        return None

    def vertical_meters(self) -> Optional[int]:
        """
        Parses vertical meters gained throughout the stage from HTML.

        :return: Vertical meters.
        """
        vert_meters = self._stage_info_by_label("Vert")
        if vert_meters:
            return int(vert_meters)
        return None

    def date(self) -> str:
        """
        Parses date when stage took place from HTML.

        :return: Date when stage took place in ``YYYY-MM-DD`` format.
        """
        date = self._stage_info_by_label("Date")
        return convert_date(date.split(", ")[0])

    def departure(self) -> str:
        """
        Parses departure of the stage from HTML.

        :return: Departure of the stage.
        """
        return self._stage_info_by_label("Departure")

    def arrival(self) -> str:
        """
        Parses arrival of the stage from HTML.

        :return: Arrival of the stage.
        """
        return self._stage_info_by_label("Arrival")

    def won_how(self) -> str:
        """
        Parses won how string from HTML.

        :return: Won how string e.g ``Sprint of small group``.
        """
        return self._stage_info_by_label("Won how")

    def race_startlist_quality_score(self) -> int:
        """
        Parses race startlist quality score from HTML.

        :return: Race startlist quality score.
        """
        return int(self._stage_info_by_label("Startlist quality score"))

    def profile_score(self) -> Optional[int]:
        """
        Parses profile score from HTML.

        :return: Profile score.
        """
        profile_score = self._stage_info_by_label("Profile")
        if profile_score:
            return int(profile_score)
        return None


    def pcs_points_scale(self) -> str:
        """
        Parses PCS points scale from HTML.

        :return: PCS points scale, e.g. ``GT.A.Stage``.
        """
        return self._stage_info_by_label("Points scale")

    def uci_points_scale(self) -> str:
        """
        Parses UCI points scale from HTML.

        :return: UCI points scale, e.g. ``UCI scale``. Empty string when not
            found.
        """
        scale_str = self._stage_info_by_label("UCI scale")
        if scale_str:
            return scale_str.split()[0]
        return scale_str
      
    def avg_speed_winner(self) -> Optional[float]:
        """
        Parses average speed winner from HTML.

        :return: avg speed winner, e.g. ``44.438``.
        """
        speed_str = self._stage_info_by_label("Avg. speed winner")
        if speed_str:
            return float(speed_str.split(" ")[0])
        else:
            return None

    def avg_temperature(self) -> Optional[float]:
        """
        Parses average temperature from HTML.

        :return: avg temperature, e.g. ``20``.
        """
        temp_str = self._stage_info_by_label("Avg. temperature")
        if temp_str:
            return float(temp_str.split(" ")[0])
        else:
            return None

    def start_time(self) -> str:
        """
        Parses start time from HTML.

        :return: start time, e.g. ``17:00 (17:00 CET)``.
        """
        return self._stage_info_by_label("Start time")

    def race_category(self) -> str:
        """
        Parses race category from HTML.

        :return: race category, e.g. ``ME - Men Elite``.
        """
        return self._stage_info_by_label("Race category")
      
    def climbs(self, *args: str) -> List[Dict[str, str]]:
        """
        Parses listed climbs from the stage. When climbs aren't listed returns
        empty list.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - climb_name:
            - climb_url: URL of the location of the climb, NOT the climb itself

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "climb_name",
            "climb_url"
        )
        fields = parse_table_fields_args(args, available_fields)
        climbs_html = self.html.css_first("ul.list.circle")
        if climbs_html is None:
            return []

        table_parser = TableParser(climbs_html)
        table_parser.parse(fields)
        return table_parser.table

    def results(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses main results table from HTML. If results table is TTT one day
        race, fields `age` and `nationality` are set to None if are requested,
        because they aren't contained in the HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - rider_number:
            - team_name:
            - team_url:
            - rank: Rider's result in the stage.
            - status: ``DF``, ``DNF``, ``DNS``, ``OTL`` or ``DSQ``.
            - age: Rider's age.
            - nationality: Rider's nationality as 2 chars long country code.
            - time: Rider's time in the stage.
            - bonus: Bonus seconds in `H:MM:SS` time format.
            - pcs_points:
            - uci_points:

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rider_name",
            "rider_url",
            "rider_number",
            "team_name",
            "team_url",
            "rank",
            "status",
            "age",
            "nationality",
            "time",
            "bonus",
            "pcs_points",
            "uci_points"
        )
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        # because of one day races self._table_index isn't used here
        categories = self.html.css(self._tables_path)
        results_table_html = categories[0]
        # Results table is empty
        if (not results_table_html or
            not results_table_html.css_first("tbody > tr")):
            raise ExpectedParsingError("Results table not in page HTML")
        # parse TTT table
        if self.stage_type() == "TTT":
            table = self._ttt_results(results_table_html, fields)
            # set status of all riders to DF because status information isn't
            # contained in the HTML of TTT results
            if "status" in fields:
                for row in table:
                    row['status'] = "DF"
            # add extra elements from GC table if possible and needed
            gc_table_html = self._table_html("gc")
            if (not self.is_one_day_race() and gc_table_html and
                ("nationality" in fields or "age" in fields)):
                table_parser = TableParser(gc_table_html)
                extra_fields = [f for f in fields
                                if f in ("nationality", "age", "rider_url")]
                # add rider_url for table joining purposes
                extra_fields.append("rider_url")
                table_parser.parse(extra_fields)
                table = join_tables(table, table_parser.table, "rider_url",
                    True)
            elif "nationality" in fields or "age" in fields or \
                "rider_number" in fields:
                for row in table:
                    if "nationality" in fields:
                        row['nationality'] = None
                    if "age" in fields:
                        row['age'] = None
                    if "rider_number" in fields:
                        row['rider_number'] = None
            # remove rider_url from table if isn't needed
            if "rider_url" not in fields:
                for row in table:
                    row.pop("rider_url")
        else:
            table_parser = TableParser(results_table_html)
            table_parser.parse(fields)
            table = table_parser.table
        return table

    def gc(self, *args: str) -> List[Dict[str, Any]]: \
        # pylint: disable=invalid-name
        """
        Parses GC results table from HTML. When GC is unavailable, empty list
        is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - rider_number:
            - team_name:
            - team_url:
            - rank: Rider's GC rank after the stage.
            - prev_rank: Rider's GC rank before the stage.
            - age: Rider's age.
            - nationality: Rider's nationality as 2 chars long country code.
            - time: Rider's GC time after the stage.
            - bonus: Bonus seconds that the rider gained throughout the race.
            - pcs_points:
            - uci_points:

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rider_name",
            "rider_url",
            "rider_number",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "age",
            "nationality",
            "time",
            "bonus",
            "pcs_points",
            "uci_points"
        )
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        gc_table_html = self._table_html("gc")
        if not gc_table_html:
            return []
        table_parser = TableParser(gc_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def points(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses points classification results table from HTML. When points
        classif. is unavailable empty list is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - rider_number:
            - team_name:
            - team_url:
            - rank: Rider's points classif. rank after the stage.
            - prev_rank: Rider's points classif. rank before the stage.
            - points: Rider's points classif. points after the stage.
            - age: Rider's age.
            - nationality: Rider's nationality as 2 chars long country code.
            - pcs_points:
            - uci_points:

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rider_name",
            "rider_url",
            "rider_number",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "points",
            "age",
            "nationality",
            "pcs_points",
            "uci_points"
        )
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        points_table_html = self._table_html("points")
        if not points_table_html:
            return []
        table_parser = TableParser(points_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def kom(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses KOM classification results table from HTML. When KOM classif. is
        unavailable empty list is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - rider_number:
            - team_name:
            - team_url:
            - rank: Rider's KOM classif. rank after the stage.
            - prev_rank: Rider's KOM classif. rank before the stage.
            - points: Rider's KOM points after the stage.
            - age: Rider's age.
            - nationality: Rider's nationality as 2 chars long country code.
            - pcs_points:
            - uci_points:

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rider_name",
            "rider_url",
            "rider_number",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "points",
            "age",
            "nationality",
            "pcs_points",
            "uci_points"
        )
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        kom_table_html = self._table_html("kom")
        if not kom_table_html:
            return []
        table_parser = TableParser(kom_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def youth(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses youth classification results table from HTML. When youth classif
        is unavailable empty list is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - rider_number:
            - team_name:
            - team_url:
            - rank: Rider's youth classif. rank after the stage.
            - prev_rank: Rider's youth classif. rank before the stage.
            - time: Rider's GC time after the stage.
            - age: Rider's age.
            - nationality: Rider's nationality as 2 chars long country code.
            - pcs_points:
            - uci_points:

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rider_name",
            "rider_url",
            "rider_number",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "time",
            "age",
            "nationality",
            "pcs_points",
            "uci_points"
        )
        fields = parse_table_fields_args(args, available_fields)
        youth_table_html = self._table_html("youth")
        if not youth_table_html:
            return []
        table_parser = TableParser(youth_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def teams(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses teams classification results table from HTML. When teams
        classif. is unavailable empty list is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - team_name:
            - team_url:
            - rank: Teams's classif. rank after the stage.
            - prev_rank: Team's classif. rank before the stage.
            - time: Team's total GC time after the stage.
            - nationality: Team's nationality as 2 chars long country code.

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "time",
            "nationality"
        )
        fields = parse_table_fields_args(args, available_fields)
        teams_table_html = self._table_html("teams")
        if not teams_table_html:
            return []
        table_parser = TableParser(teams_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def _stage_info_by_label(self, label: str) -> str:
        """
        Finds infolist value for given label.

        :param label: Label to find value for.
        :return: Value of given label. Empty string when label is not in
            infolist.
        """
        for row in self.html.css("ul.infolist > li"):
            row_text = row.text(separator="\n").split("\n")
            row_text = [x for x in row_text if x != " "]
            if label in row_text[0]:
                if len(row_text) > 1:
                    return row_text[1]
                else:
                    return ""
        return ""

    def _table_html(self, table: Literal[
            "stage",
            "gc",
            "points",
            "kom",
            "youth",
            "teams"]) -> Optional[Node]:
        """
        Get HTML of a .result-cont table with results based on `table` param.

        :param table: Keyword of wanted table that occures in .restabs menu.
        :return: HTML of wanted HTML table, None when not found.
        """
        categories = self.html.css(".result-cont")
        for i, element in enumerate(self.html.css("ul.restabs > li > a")):
            if table in element.text().lower():
                return categories[i].css_first("table")
        return None

    @staticmethod
    def _ttt_results(results_table_html: Node,
                     fields: List[str]) -> List[Dict[str, Any]]:
        """
        Parses data from TTT results table.

        :param results_table_html: TTT results table HTML.
        :param fields: Fields that returned table should have. Available are
            all `results` table fields with the exception of age,
            nationality and rider_number.
        :return: Table with wanted fields.
        """
        team_fields = [
            "rank",
            "team_name",
            "team_url",
        ]
        rider_fields = [
            "rank",
            "rider_name",
            "rider_url",
            "pcs_points",
            "uci_points",
            "bonus"
        ]
        team_fields_to_parse = [f for f in team_fields if f in fields]
        rider_fields_to_parse = [f for f in rider_fields if f in fields]

        # add rank field to fields for joining tables purposes
        if "rank" not in fields:
            rider_fields_to_parse.append("rank")
            team_fields_to_parse.append("rank")
        # add rider_url for joining table with nationality or age from other
        # table, if isn't nedded is removed from table in self.results method
        if "rider_url" not in fields:
            rider_fields_to_parse.append("rider_url")

        # create two copies of HTML table (one for riders and one for teams),
        # so we won't modify self.html
        riders_elements = HTMLParser(results_table_html.html) # type: ignore
        riders_table = riders_elements.css_first("table")
        teams_elements = HTMLParser(results_table_html.html) # type: ignore
        teams_table = teams_elements.css_first("table")
        # remove unwanted rows from both tables
        riders_table.unwrap_tags(["tr.team"])
        teams_table.unwrap_tags(["tr:not(.team)"])
        teams_parser = TableParser(teams_table)
        teams_parser.parse(team_fields_to_parse)
        riders_parser = TableParser(riders_table)
        riders_parser.parse(rider_fields_to_parse)

        # add time of every rider to the table
        if "time" in fields:
            team_times = teams_parser.parse_extra_column("Time", format_time)
            # riders extra times from second HTML table column, if there is no
            # extra time, time is set to None
            riders_extra_times = riders_parser.parse_extra_column(1,
                lambda x: format_time(x.split("+")[1]) if
                len(x.split("+")) >= 2 else "0:00:00")

            riders_parser.extend_table("rider_time", riders_extra_times)
            teams_parser.extend_table("time", team_times)

            table = join_tables(riders_parser.table, teams_parser.table,
                "rank")
            # add team times and rider_extra times together and remove
            # rider_time field from table
            for row in table:
                rider_extra_time = row.pop('rider_time')
                row['time'] = add_times(row['time'], rider_extra_time)
        else:
            table = join_tables(riders_parser.table, teams_parser.table,
                "rank")
        # sort by name for consistent testing results (url is in fields by
        # default)
        table.sort(key = lambda x: x['rider_url'])
        # sort by rank to get default rank order
        table.sort(key = lambda x: x['rank'])
        if "rank" not in fields:
            for row in table:
                row.pop("rank")
        # for row in table:
        #     print(row['rider_url'])
        return table
