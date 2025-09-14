import re
from typing import Any, Dict, List, Literal, Optional, Tuple

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
    _tables_path = ".resultCont .resTab .general table.results"

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is an one day race from HTML.

        :return: Whether the race is an one day race.
        """
        # If there are elements with .restabs class (Stage/GC... menu), the race
        # is a stage race
        return len(self.html.css(".restabs")) == 0 and len(self.html.css(".resultTabs")) == 0

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
        page_title = self.html.css_first(".page-title")
        if not page_title:
            raise ExpectedParsingError("Page title not found")
        page_title_text = page_title.text(strip=True)
        if "ITT" in page_title_text:
            return "ITT"
        elif "TTT" in page_title_text:
            return "TTT"
        return "RR"
       
    def vertical_meters(self) -> Optional[int]:
        """
        Parses vertical meters gained throughout the stage from HTML.

        :return: Vertical meters.
        """
        vert_meters = self._stage_info_by_label("Vert")
        if vert_meters:
            return int(vert_meters)
        return None

    def avg_temperature(self) -> Optional[float]:
        """
        Parses average temperature during the stage from the HTML.

        :return: Average temperature in degree celsius as float.
        """
        temp_str1 = self._stage_info_by_label("Avg. temp")
        temp_str2 = self._stage_info_by_label("Average temp")
        if temp_str1:
            return float(temp_str1.split(" ")[0])
        elif temp_str2:
            return float(temp_str2.split(" ")[0])
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

    def race_startlist_quality_score(self) -> Tuple[int, int]:
        """
        Parses race startlist quality score from HTML.

        :return: Tuple of race startlist quality scores. The first element is
        race startlist quality score at the beginning of the race and
        the second one is quality score after current stage.
        """
        scores_str = self._stage_info_by_label("Startlist quality score")
        if len(scores_str.split()) == 1:
            return int(scores_str), int(scores_str)
        score1, score2 = scores_str.split()
        return int(score1), int(score2[1:-1])

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
        climbs_html = self._find_header_list("Climbs")
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
        # parse TTT table
        if self.stage_type() == "TTT":
            table = self._ttt_results(self.html.css_first(".ttt-results"), fields)
            # add extra elements from GC table if possible and needed
            gc_table_html = self._table_html("gc")
            if (not self.is_one_day_race() and gc_table_html and
                ("nationality" in fields or "age" in fields or "rider_number" in fields)):
                table_parser = TableParser(gc_table_html)
                extra_fields = [f for f in fields
                                if f in ("nationality", "age", "rider_number", "rider_url")]
                # add rider_url for table joining purposes
                extra_fields.append("rider_url")
                table_parser.parse(extra_fields)
                table = join_tables(table, table_parser.table, "rider_url", True)
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
            categories = self.html.css(self._tables_path)
            if not categories:
                fallback = self.html.css('.general > table.results')
            if fallback:
                categories = [fallback[0]]
            else:
                raise ExpectedParsingError("Results table not in page HTML")
            results_table_html = categories[0]
            # Results table is empty
            if (not results_table_html or
                not results_table_html.css_first("tbody > tr")):
                raise ExpectedParsingError("Results table not in page HTML")
            # remove rows that aren't results
            for row in results_table_html.css("tbody > tr"):
                columns = row.css("td")
                if len(columns) <= 2 and columns[0].text() == "" or \
                        "relegated from" in columns[0].text():
                    row.remove()
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
        stage_info = self._find_header_list("Race information")
        for row in stage_info.css("li"):
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
        Get HTML of a .resTab table with results based on `table` param.

        :param table: Keyword of wanted table that occurs in result tabs.
        :return: HTML of wanted HTML table, None when not found.
        """
        # Map table names to their corresponding tab identifiers
        tab_mapping = {
            "stage": ["STAGE", "stage"],
            "gc": ["GC", "gc"], 
            "points": ["POINTS", "points"],
            "kom": ["KOM", "kom"],
            "youth": ["YOUTH", "youth"],
            "teams": ["TEAMS", "teams"]
        }
        
        # Look for tabs in the results section
        tab_nav = self.html.css("ul.tabs.tabnav.resultTabs li")
        if not tab_nav:
            # Fallback to old tab structure
            tab_nav = self.html.css("ul.restabs li")
        
        for tab_element in tab_nav:
            tab_link = tab_element.css_first("a")
            if not tab_link:
                continue
                
            tab_text = tab_link.text().upper()
            tab_keywords = tab_mapping.get(table, [])
            
            # Check if this tab matches what we're looking for
            if any(keyword.upper() in tab_text for keyword in tab_keywords):
                # Get the data-id from the tab link
                data_id = tab_link.attributes.get("data-id")
                if data_id:
                    # Find corresponding result div
                    result_div = self.html.css_first(f'div.resTab[data-id="{data_id}"]')
                    if result_div:
                        return result_div.css_first("table.results")
        
        # Fallback: look for result containers directly (old structure)
        result_containers = self.html.css(".result-cont")
        if result_containers and table == "stage":
            # First container is usually stage results
            return result_containers[0].css_first("table")
        
        # Additional fallback for direct table lookup
        if table == "stage":
            stage_table = self.html.css_first("div.resTab table.results")
            if stage_table:
                return stage_table
            
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
        table = []
        for row in results_table_html.css("li")[1:]:
            rank = row.css_first("div > div").text().split()[0]
            team_name = row.css_first("a").text()
            time = format_time(row.css_first("div.time").text())
            team_url = row.css_first("a").attributes['href']
            for tr_el in row.css("tbody > tr"):
                table.append({})
                rider_url = tr_el.css_first("a").attributes['href']
                table[-1]["rider_url"] = rider_url
                if "rider_name" in fields:
                    rider_name = tr_el.css_first("a").text()
                    table[-1]["rider_name"] = rider_name
                if "pcs_points" in fields:
                    pcs_points = tr_el.css_first("td.w7").text()
                    if not pcs_points:
                        pcs_points = 0
                    table[-1]["pcs_points"] = float(pcs_points)
                if "uci_points" in fields:
                    table[-1]["uci_points"] = float(0)
                if "team_name" in fields:
                    table[-1]["team_name"] = team_name
                if "team_url" in fields:
                    table[-1]["team_url"] = team_url
                if "time" in fields:
                    table[-1]["time"] = time
                if "bonus" in fields:
                    table[-1]["bonus"] = "0:00:00"
                if "status" in fields:
                    table[-1]["status"] = "DF"
                if "rank" in fields:
                    table[-1]["rank"] = rank
        return table
