from typing import Any, Dict, List, Literal, Optional, Tuple

from selectolax.parser import HTMLParser, Node

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import (add_times, convert_date, format_regex_str, format_time,
                    join_tables, parse_table_fields_args, reg)


class Stage(Scraper):
    """
    Scraper for stage results HTML page. Example URL:
    `race/tour-de-france/2022/stage-18`.
    """
    _url_validation_regex = format_regex_str(
    f"""
        {reg.base_url}?race{reg.url_str}
        ({reg.year}{reg.stage}({reg.result}{reg.anything}?)?|
        ({reg.year}{reg.result}?({reg.result}{reg.result}{reg.anything})?)|
        ({reg.result}{reg.anything}))?
        \\/*
    """)
    """Regex for validating stage URL."""
    _tables_path = ".result-cont table"

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. Determines equality of objects (is
        used in `__eq__` method).

        :return: Normalized URL in `race/{race_id}/{year}/{stage_id}` format.
        When year or stage_id aren't contained in user defined URL, they are
        skipped.
        """
        decomposed_url = self._decompose_url()
        decomposed_url.extend([""] * (4 - len(decomposed_url)))
        race_id = decomposed_url[1]
        if decomposed_url[2].isnumeric() and len(decomposed_url[2]) == 4:
            year = decomposed_url[2]
        else:
            year = None
        if "stage" in decomposed_url[3] or "prologue" in decomposed_url[3]:
            stage_id = decomposed_url[3]
        else:
            stage_id = None
        normalized_url = f"race/{race_id}"
        if year is not None:
            normalized_url += f"/{year}"
            if stage_id is not None:
                normalized_url += f"/{stage_id}"
        return normalized_url

    def _set_up_html(self) -> None:
        """
        Overrides Scraper method. Modifies HTML if stage is TTT by adding team
        ranks to riders.
        """
        # add team ranks to every rider's first td element, so it's possible
        # to map teams to riders based on their rank
        categories = self.html.css(self._tables_path)
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
        Parses whether race is an one day race from HTML

        :return: whether the race is an one day race
        """
        # If there are elements with .restabs class (Stage/GC... menu), the race
        # is a stage race
        return len(self.html.css(".restabs")) == 0

    def distance(self) -> float:
        """
        Parses stage distance from HTML

        :return: stage distance in kms
        """
        distance_html = self.html.css_first(
            ".infolist > li:nth-child(5) > div:nth-child(2)")
        return float(distance_html.text().split(" km")[0])

    def profile_icon(self) -> Literal["p0", "p1", "p2", "p3", "p4", "p5"]:
        """
        Parses profile icon from HTML

        :return: profile icon e.g. `p4`, the higher the number is the more
        difficult the profile is
        """
        profile_html = self.html.css_first("span.icon")
        return profile_html.attributes['class'].split(" ")[2] # type: ignore

    def stage_type(self) -> Literal["ITT", "TTT", "RR"]:
        """
        Parses stage type from HTML

        :return: stage type
        """
        stage_name_html = self.html.css_first(".sub > .blue")
        stage_name2_html = self.html.css_first("div.main > h1")
        stage_name = stage_name_html.text()
        stage_name2 = stage_name2_html.text()
        if "ITT" in stage_name or "ITT" in stage_name2:
            return "ITT"
        elif "TTT" in stage_name or "TTT" in stage_name2:
            return "TTT"
        else:
            return "RR"

    def winning_attack_length(self, when_none_or_unknown: float = 0.0) -> float:
        """
        Parses length of winning attack from HTML

        :param when_none_or_unknown: value to return when there is no info
        about winning attack, defaults to 0.0
        :return: length of winning attack"""
        won_how_html = self.html.css_first(
            ".infolist > li:nth-child(12) > div:nth-child(2)")
        won_how = won_how_html.text()
        if " km solo" in won_how:
            return float(won_how.split(" km sol")[0])
        else:
            return when_none_or_unknown

    def vertical_meters(self) -> Optional[int]:
        """
        Parses vertical meters gained throughout the stage from HTML

        :return: vertical meters
        """
        vertical_meters_html = self.html.css_first(
            ".infolist > li:nth-child(9) > div:nth-child(2)")
        vertical_meters = vertical_meters_html.text()
        return int(vertical_meters) if vertical_meters else None

    def date(self) -> str:
        """
        Parses date when stage took place from HTML

        :return: date when stage took place `YYYY-MM-DD`
        """
        date_html = self.html.css_first(".infolist > li > div:nth-child(2)")
        date = date_html.text().split(", ")[0]
        return convert_date(date)

    def departure(self) -> str:
        """
        Parses departure of the stage from HTML

        :return: departure of the stage
        """
        departure_html = self.html.css_first(
            ".infolist > li:nth-child(10) > div:nth-child(2)")
        return departure_html.text()

    def arrival(self) -> str:
        """
        Parses arrival of the stage from HTML

        :return: arrival of the stage
        """
        arrival_html = self.html.css_first(
            ".infolist > li:nth-child(11) > div:nth-child(2)")
        return arrival_html.text()

    def results(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "status",
            "age",
            "nationality",
            "time",
            "bonus",
            "pcs_points",
            "uci_points")) -> List[Dict[str, Any]]:
        """
        Parses main results table from HTML. If results table is TTT one day
        race, fields `age` and `nationality` are set to None if are requested,
        because they aren't contained in the HTML.

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: results table represented as list of dicts
        """
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
                table = join_tables(table, table_parser.table, "rider_url")
            elif "nationality" in fields or "age" in fields:
                for row in table:
                    row['nationality'] = None
                    row['age'] = None
            # remove rider_url from table if isn't needed
            if "rider_url" not in fields:
                for row in table:
                    row.pop("rider_url")
        else:
            table_parser = TableParser(results_table_html)
            table_parser.parse(fields)
            table = table_parser.table
        return table

    def gc(self, *args: str, available_fields: Tuple[str, ...] = ( \
        # pylint: disable=invalid-name
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "age",
            "nationality",
            "time",
            "bonus",
            "pcs_points",
            "uci_points")) -> List[Dict[str, Any]]:
        """
        Parses results from GC results table from HTML, available only on stage
        races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: GC results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        gc_table_html = self._table_html("gc")
        if not gc_table_html:
            raise ExpectedParsingError("GC table not in page HTML")
        table_parser = TableParser(gc_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def points(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "points",
            "age",
            "nationality",
            "pcs_points",
            "uci_points")) -> List[Dict[str, Any]]:
        """
        Parses results from points classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: points classification results table represented as list of
        dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        points_table_html = self._table_html("points")
        if not points_table_html:
            raise ExpectedParsingError("Points table not in page HTML")
        table_parser = TableParser(points_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def kom(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "points",
            "age",
            "nationality",
            "pcs_points",
            "uci_points")) -> List[Dict[str, Any]]:
        """
        Parses results from KOM classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: KOM classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        # remove other result tables from html
        kom_table_html = self._table_html("kom")
        if not kom_table_html:
            raise ExpectedParsingError("KOM table not in page HTML")
        table_parser = TableParser(kom_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def youth(self, *args: str, available_fields: Tuple[str, ...] = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "time",
            "age",
            "nationality",
            "pcs_points",
            "uci_points")) -> List[Dict[str, Any]]:
        """
        Parses results from youth classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: youth classification results table represented as list of dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        youth_table_html = self._table_html("youth")
        if not youth_table_html:
            raise ExpectedParsingError("Youth table not in page HTML")
        table_parser = TableParser(youth_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def teams(self, *args: str, available_fields: Tuple[str, ...] = (
            "team_name",
            "team_url",
            "rank",
            "prev_rank",
            "time",
            "nationality")) -> List[Dict[str, Any]]:
        """
        Parses results from teams classification results table from HTML,
        available only on stage races

        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :return: youth classification results table represented as list of
        dicts
        """
        fields = parse_table_fields_args(args, available_fields)
        teams_table_html = self._table_html("teams")
        if not teams_table_html:
            raise ExpectedParsingError("Teams table not in page HTML")
        table_parser = TableParser(teams_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def _table_html(self, table: Literal[
            "stage",
            "gc",
            "points",
            "kom",
            "youth",
            "teams"]) -> Optional[Node]:
        """
        Get HTML of a .result-cont table with results based on `table` param

        :param table: keyword of wanted table that occures in .restabs menu
        :return: HTML of wanted HTML table, None when not found
        """
        categories = self.html.css(".result-cont")
        for i, element in enumerate(self.html.css("ul.restabs > li > a")):
            if table in element.text().lower():
                return categories[i].css_first("table")

    @staticmethod
    def _ttt_results(results_table_html: Node,
                     fields: List[str]) -> List[Dict[str, Any]]:
        """
        Parses data from TTT results table.

        :param results_table_html: TTT results table HTML
        :param fields: fields that returned table should have
        :return: table represented as list of dicts
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
        if "rank" not in fields:
            for row in table:
                row.pop("rank")
        return table
