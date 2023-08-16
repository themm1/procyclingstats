import re
from typing import Any, Dict, List, Literal, Tuple

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import parse_select, parse_table_fields_args, select_menu_by_name


class Ranking(Scraper):
    """
    Scraper for rankings HTML page.

    Always only one parsing method that parses ranking is availabe, the others
    raise `ExpectedParsingError`. E.g. for object created with example URL
    would be valid only `self.individual_ranking` parsing method and others
    methods that parse ranking (`self.team_ranking`, ...) would raise error.

    Usage:

    >>> from procyclingstats import Ranking
    >>> ranking = Ranking("rankings/me/individual")
    >>> ranking.individual_ranking()
    [
        {
            'nationality': 'SI',
            'points': 2981.0,
            'prev_rank': 1,
            'rank': 1,
            'rider_name': 'Pogačar Tadej',
            'rider_url': 'rider/tadej-pogacar',
            'team_name': 'UAE Team Emirates',
            'team_url': 'team/uae-team-emirates-2022'
        },
        ...
    ]
    >>> ranking.parse()
    {
        'dates_select': [
            {'text': '2022-09-11', 'value': '2022-09-11'},
            {'text': '2021-12-31', 'value': '2021-12-31'},
            {'text': '2019-12-31', 'value': '2019-12-31'},
            ...
        ],
        'distance_ranking': None,
        'individual_ranking': [
            {
                'nationality': 'SI',
                'points': 2981.0,
                'prev_rank': 1,
                'rank': 1,
                'rider_name': 'Pogačar Tadej',
                'rider_url': 'rider/tadej-pogacar',
                'team_name': 'UAE Team Emirates',
                'team_url': 'team/uae-team-emirates-2022'
            },
            ...
        ],
        'individual_wins_ranking': None,
        ...
    }
    """
    def individual_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses individual ranking from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - team_name:
            - team_url:
            - rank: Rider's rank in the ranking.
            - prev_rank: Rider's rank in previous ranking update.
            - nationality: Rider's nationality as 2 chars long country code.
            - points:

        :raises ExpectedParsingError: When the table from HTML is not an
            individual points ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rank",
            "prev_rank",
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "nationality",
            "points"
        )
        if self._ranking_type() != "individual":
            raise ExpectedParsingError(
                "This object doesn't support individual_ranking method, create"
                "one with individual ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def team_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses team ranking from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - team_name:
            - team_url:
            - rank: Team's rank in the ranking.
            - prev_rank: Team's rank in previous ranking update.
            - nationality: Team's nationality as 2 chars long country code.
            - class: Team's class, e.g. ``WT``.
            - points:

        :raises ExpectedParsingError: When the table from HTML is not a team
            points ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rank",
            "prev_rank",
            "team_name",
            "team_url",
            "nationality",
            "class",
            "points"
        )
        if self._ranking_type() != "teams":
            raise ExpectedParsingError(
                "This object doesn't support team_ranking method, "
                "create one with teams ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def nations_ranking(self, *args: str) -> List[Dict[str, Any]]:

        """
        Parses nations ranking from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - nation_name:
            - nation_url:
            - rank: Nation's rank in the ranking.
            - prev_rank: Nation's rank in previous ranking update.
            - nationality: Nation as 2 chars long country code.
            - points:

        :raises ExpectedParsingError: When the table from HTML is not a
            nationality points ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rank",
            "prev_rank",
            "nation_name",
            "nation_url",
            "nationality",
            "points"
        )
        if self._ranking_type() != "nations":
            raise ExpectedParsingError(
                "This object doesn't support nations_ranking method, create" +
                "one with nations ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def races_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses race ranking from HTML. Race points are evaluated based on
            startlist quality score.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - race_name:
            - race_url:
            - rank: Race's rank in the ranking.
            - prev_rank: Race's rank in previous ranking update.
            - nationality: Race's nationality as 2 chars long country code.
            - class: Race's class, e.g. ``WT``.
            - points:

        :raises ExpectedParsingError: When the table from HTML is not a race
            ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rank",
            "prev_rank",
            "race_name",
            "race_url",
            "nationality",
            "class",
            "points"
        )
        if self._ranking_type() != "races":
            raise ExpectedParsingError(
                "This object doesn't support races_ranking method, create one"
                "with race ranking URL to call this method.")

        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.css_first("table")
        table_parser = TableParser(html_table)
        # parse race name and url as stage name and url and rename it
        # afterwards
        if "race_name" in fields:
            fields[fields.index("race_name")] = "stage_name"
        if "race_url" in fields:
            fields[fields.index("race_url")] = "stage_url"
        table_parser.parse(fields)
        table_parser.rename_field("stage_name", "race_name")
        table_parser.rename_field("stage_url", "race_url")
        return table_parser.table

    def individual_wins_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses individual wins ranking from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - team_name:
            - team_url:
            - rank: Rider's rank in the ranking.
            - prev_rank: Rider's rank in previous ranking update.
            - nationality: Rider's nationality as 2 chars long country code.
            - first_places:
            - second_places:
            - third_places:

        :raises ExpectedParsingError: When the table from HTML is not an
            individual wins ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rank",
            "prev_rank",
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "nationality",
            "first_places",
            "second_places",
            "third_places"
        )
        if self._ranking_type() != "individual_wins":
            raise ExpectedParsingError(
                "This object doesn't support races_ranking method, create one"
                "with individual wins ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def teams_wins_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses team wins ranking from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - team_name:
            - team_url:
            - rank: Team's rank in the ranking.
            - prev_rank: Team's rank in previous ranking update.
            - nationality: Team's nationality as 2 chars long country code.
            - class: Team's class, e.g. ``WT``.
            - first_places:
            - second_places:
            - third_places:

        :raises ExpectedParsingError: When the table from HTML is not a team
            wins ranking.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rank",
            "prev_rank",
            "team_name",
            "team_url",
            "nationality",
            "class",
            "first_places",
            "second_places",
            "third_places"
        )
        if self._ranking_type() != "team_wins":
            raise ExpectedParsingError(
                "This object doesn't support teams_wins_ranking method, "
                "create one with teams wins ranking URL to call this method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def nations_wins_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses nations wins ranking from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - nation_name:
            - nation_url:
            - rank: Nation's rank in the ranking.
            - prev_rank: Nation's rank in previous ranking update.
            - nationality: Nation as 2 chars long country code.
            - first_places:
            - second_places:
            - third_places:

        :raises ExpectedParsingError: When the table from HTML is not a nation
            wins ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rank",
            "prev_rank",
            "nation_name",
            "nation_url",
            "nationality",
            "first_places",
            "second_places",
            "third_places"
        )

        if self._ranking_type() != "nation_wins":
            raise ExpectedParsingError(
                "This object doesn't support nations_wins_ranking method, " +
                "create one with nations wins ranking URL to call this" +
                "method.")
        return self._parse_regular_ranking_table(args, available_fields)

    def distance_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses ranking with riders ridden distances from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - team_name:
            - team_url:
            - rank: Rider's rank in the ranking.
            - nationality: Rider's nationality as 2 chars long country code.
            - distance: Rider's ridden distance in the season as KMs.

        :raises ExpectedParsingError: When the table from HTML is not a
            distance ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "nationality",
            "distance",
        )
        if self._ranking_type() != "distance":
            raise ExpectedParsingError(
                "This object doesn't support distance_ranking method, " +
                "create one with distance ranking URL to call this" +
                "method.")
        fields = parse_table_fields_args(args, available_fields)
        casual_fields = [f for f in fields if f not in ("distance")]

        distance_ranking_table_html = self.html.css_first("span > table")
        table_parser = TableParser(distance_ranking_table_html)
        table_parser.parse(casual_fields)

        if "distance" in fields:
            distances = table_parser.parse_extra_column("KMs",
                lambda x: int(x) if x else 0)
            table_parser.extend_table("distance", distances)
        return table_parser.table

    def racedays_ranking(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses ranking with riders ridden racedays from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name:
            - rider_url:
            - team_name:
            - team_url:
            - rank: Rider's rank in the ranking.
            - nationality: Rider's nationality as 2 chars long country code.
            - racedays: Rider's ridden racedays in the season.

        :raises ExpectedParsingError: When the table from HTML is not a
            racedays ranking table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "rider_name",
            "rider_url",
            "team_name",
            "team_url",
            "rank",
            "nationality",
            "racedays",
        )
        if self._ranking_type() != "racedays":
            raise ExpectedParsingError(
                "This object doesn't support distance_ranking method, " +
                "create one with distance ranking URL to call this" +
                "method.")
        fields = parse_table_fields_args(args, available_fields)
        casual_fields = [f for f in fields if f not in ("racedays")]

        distance_ranking_table_html = self.html.css_first("span > table")
        table_parser = TableParser(distance_ranking_table_html)
        table_parser.parse(casual_fields)

        if "racedays" in fields:
            racedays = table_parser.parse_extra_column("Racedays",
                lambda x: int(x) if x else 0)
            table_parser.extend_table("racedays", racedays)
        return table_parser.table

    def dates_select(self) -> List[Dict[str, str]]:
        """
        Parses dates select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "date"))

    def nations_select(self) -> List[Dict[str, str]]:
        """
        Parses nations select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "nation"))

    def teams_select(self) -> List[Dict[str, str]]:
        """
        Parses teams select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "team"))

    def pages_select(self) -> List[Dict[str, str]]:
        """
        Parses pages select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "offset"))

    def teamlevels_select(self) -> List[Dict[str, str]]:
        """
        Parses team levels select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "teamlevel"))

    def _ranking_type(self) -> Literal["individual",
                                       "nations",
                                       "teams",
                                       "races",
                                       "distance",
                                       "racedays",
                                       "individual_wins",
                                       "team_wins",
                                       "nation_wins"]:
        """
        Finds out what is the ranking type of the object based on URL

        :return: Ranking type.
        """

        relative_url = self.relative_url()
        if len(relative_url.split("/")) < 3 and "?" not in relative_url:
            return "individual"
        if "races" in relative_url:
            l = [m.start() for m in re.finditer("races", relative_url)]
            if relative_url[l[0] - 1] != "-":
                return "races"
        if "distance" in relative_url:
            return "distance"
        if "racedays" in relative_url:
            return "racedays"
        if "wins-individual" in relative_url:
            return "individual_wins"
        if "wins-teams" in relative_url:
            return "team_wins"
        if "wins-nations" in relative_url:
            return "nation_wins"
        if "nations" in relative_url:
            return "nations"
        if "teams" in relative_url:
            return "teams"
        return "individual"

    def _parse_regular_ranking_table(self,
            args: Tuple[str, ...],
            available_fields: Tuple[str, ...]) -> List[Dict[str, Any]]:
        """
        Does general ranking parsing procedure using TableParser.

        :param args: Parsing method args (only the ones that
            `TableParser.parse` method is able to parse).
        :param available_fields: Available table fields for parsing method
        :return: Table with wanted fields.
        """
        fields = parse_table_fields_args(args, available_fields)
        html_table = self.html.css_first("table")
        table_parser = TableParser(html_table)
        table_parser.parse(fields)
        return table_parser.table
