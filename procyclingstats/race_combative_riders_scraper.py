from typing import Dict, List

from .scraper import Scraper
from .table_parser import TableParser
from .utils import parse_table_fields_args

class RaceCombativeRiders(Scraper):
    """
    Scraper for combative riders HTML page.

    Usage:

    >>> from procyclingstats import RaceCombativeRiders
    >>> combative = RaceCombativeRiders("race/tour-de-france/2024/results/comative-riders")
    >>> combative.combative_riders()
    [
        {
            'stage_name': 'Stage 1',
            'stage_url': 'race/tour-de-france/2024/stage-1',
            'rider_name': 'VAN DEN BROEK Frank',
            'rider_url': 'rider/frank-van-den-broek',
            'nationality': 'NL'
        }, 
        ...
    }

    """

    def combative_riders(self, *args: str) -> List[Dict[str, str]]:
        """
        Parses combative riders from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - stage_name: Name of the stage, e.g \
                ``Stage 7 (ITT)``.
            - stage_url: URL of the stage, e.g. \
                ``race/tour-de-france/2022/stage-2``.
            - rider_name:
            - rider_url:
            - nationality: Rider's nationality as 2 chars long country code.

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "stage_name",
            "stage_url",
            "rider_name",
            "rider_url",
            "nationality"
        )
        fields = parse_table_fields_args(args, available_fields)
        # Locate the table of combative riders
        riders_table_html = self.html.css_first("table.basic")
        if not riders_table_html:
            return []

        table_parser = TableParser(riders_table_html)
        nationality_present = False
        if "nationality" in fields:
            fields.remove("nationality")
            nationality_present = True
        table_parser.parse(fields)
        if nationality_present:
            nationalities = table_parser.nationality()
            idx = 0
            for i, row in enumerate(table_parser.table):
                if row['rider_name']:
                    table_parser.table[i]['nationality'] = nationalities[idx]
                    idx += 1
                else:
                    table_parser.table[i]['nationality'] = ""
        return table_parser.table
