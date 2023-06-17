from typing import Any, Dict, List

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import parse_table_fields_args


class RaceClimbs(Scraper):
    """
    Scraper for race climbs HTML page.

    Usage:

    >>> from procyclingstats import RaceClimbs
    >>> race_climbs = RaceClimbs("race/tour-de-france/2022/gc/route/climbs")
    >>> race_climbs.climbs()
    [
        {
            'climb_name': "Côte d'Asnæs Indelukke",
            'climb_url': 'location/cote-d-asnaes-indelukke',
            'km_before_finnish': 140,
            'length': 1.1,
            'steepness': 5.3,
            'top': 63
        },
        ...
    ]
    >>> race_climbs.parse()
    {
        'climbs': [
            {
                'climb_name': "	Côte d'Asnæs Indelukke",
                'climb_url': 'location/cote-d-asnaes-indelukke',
                'km_before_finnish': 140,
                'length': 1.1,
                'steepness': 5.3,
                'top': 63
            },
            ...
        ]
    }

    """
    def _html_valid(self) -> bool:
        """
        Extends Scraper method for validating HTMLs.

        :return: True if given HTML is valid, otherwise False
        """
        return self.html.css_first("div.page-content > h2").text() == "Climbs"

    def climbs(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses race's climbs table from HTML. Note that not allways all info
        about the climbs is present (usually in older races).

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - climb_name:
            - climb_url: URL of the location of the climb, NOT the climb itself
            - length: Length of the climb in KMs.
            - steepness: Steepness of the climb in %.
            - top: Height above sea level at the top of the climb in meters.
            - km_before_finnish: KMs to finnish from the top of the climb.

        :raises ValueError: When one of args is of invalid value.
        :raises ExpectedParsingError: When climbs aren't listed on the page.
        :return: Table with wanted fields.
        """
        available_fields = (
            "climb_name",
            "climb_url",
            "length",
            "steepness",
            "top",
            "km_before_finnish"
        )
        fields = parse_table_fields_args(args, available_fields)
        table_html = self.html.css_first("table.basic")
        if table_html.css_first("tbody > tr") is None:
            raise ExpectedParsingError("Climbs aren't listed on the page.")
        table_parser = TableParser(table_html)
        casual_fields = [f for f in fields if f in ("climb_name", "climb_url")]
        table_parser.parse(casual_fields)
        if "length" in fields:
            lengths = table_parser.parse_extra_column("Length", float)
            table_parser.extend_table("length", lengths)
        if "steepness" in fields:
            lengths = table_parser.parse_extra_column("Steepness", float)
            table_parser.extend_table("steepness", lengths)
        if "top" in fields:
            lengths = table_parser.parse_extra_column("Top (m)", int)
            table_parser.extend_table("top", lengths)
        if "km_before_finnish" in fields:
            lengths = table_parser.parse_extra_column("Top at KM",
                lambda x: int(x) if x else None)
            table_parser.extend_table("km_before_finnish", lengths)
        return table_parser.table
