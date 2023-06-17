from typing import Any, Dict, List

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import parse_select, parse_table_fields_args, select_menu_by_name


class RiderResults(Scraper):
    """
    Scraper for rider results HTML page.

    Supported is besides of default results table also final 5k results table
    which can be parsed using ``final_n_km_results`` method.

    Usage:

    >>> from procyclingstats import RiderResults
    >>> rider_results = RiderResults("rider/alberto-contador/results/final-5k-analysis")
    >>> # for normal results table use "rider/alberto-contador/results" URL
    >>> rider_results.final_n_km_results()
    [
        {
            'average_percentage': 11.8,
            'class': '2.UWT',
            'date': '2017-09-09',
            'nationality': 'ES',
            'rank': 1,
            'stage_name': 'Vuelta a España | Stage 20',
            'stage_url': 'race/vuelta-a-espana/2017/stage-20',
            'vertical_meters': 590},
        },
        ...
    ]
    >>> rider_results.parse()
    {
        'categories_select': None,
        'final_n_km_results': [
            {
                'average_percentage': 11.8,
                'class': '2.UWT',
                'date': '2017-09-09',
                'nationality': 'ES',
                'rank': 1,
                'stage_name': 'Vuelta a España | Stage 20',
                'stage_url': 'race/vuelta-a-espana/2017/stage-20',
                'vertical_meters': 590},
            },
            ...
        ],
        'nations_select': None,
        ...
    }
    """
    def _html_valid(self) -> bool:
        """
        Extends Scraper method for validating HTMLs.

        :return: True if given HTML is valid, otherwise False
        """
        try:
            assert super()._html_valid()
            page_title = self.html.css_first(".page-content > h2").text()
            assert page_title in ("All results",
                "Top results final 5k analysis")
            return True
        except AssertionError:
            return False

    def _set_up_html(self):
        """Overrides Scraper method. Removes last table row with sum stats."""
        results_table_html = self.html.css_first("table")
        if not results_table_html:
            return
        for row in results_table_html.css("tr"):
            if "class" in row.attributes and row.attributes['class'] == "sum":
                row.decompose()

    def results(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses general rider's results table from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - stage_url:
            - stage_name:
            - distance:
            - nationality: Nationality of the stage race.
            - date: Date when the stage occured in ``YYYY-MM-DD`` format.
            - rank: Rider's result in the stage.
            - class: Class of the stage's race, e.g. ``2.UWT``.
            - pcs_points:
            - uci_points:

        :raises ExpecterParsingError: When the table from HTML isn't a results
            table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "date",
            "rank",
            "stage_url",
            "stage_name",
            "nationality",
            "class",
            "distance",
            "pcs_points",
            "uci_points"
        )
        if self.html.css_first(".page-content > h2").text() != "All results":
            error_msg = ("This object doesn't support 'results' method. " +
                "Create one from rider's default results table to call this " +
                "method")
            raise ExpectedParsingError(error_msg)

        fields = parse_table_fields_args(args, available_fields)
        results_table_html = self.html.css_first("table")
        table_parser = TableParser(results_table_html)
        table_parser.parse(fields)
        return table_parser.table

    def final_n_km_results(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses rider's final n KMs results table from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - stage_url:
            - stage_name:
            - nationality: Nationality of the stage race.
            - date: Date when the stage occured in ``YYYY-MM-DD`` format.
            - rank: Rider's result in the stage.
            - class: Class of the stage's race, e.g. ``2.UWT``.
            - vertical_meters: Vertical meters gained in final n KMs.
            - average_percentage: Average percentage of last n KMs.

        :raises ExpecterParsingError: When the table from HTML isn't a final n
            KMs results table.
        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "date",
            "rank",
            "stage_url",
            "stage_name",
            "nationality",
            "class",
            "vertical_meters",
            "average_percentage"
        )
        if (self.html.css_first(".page-content > h2").text() !=
                "Top results final 5k analysis"):
            error_msg = ("This object doesn't support 'final_n_km_results'" +
            "method. Create one from rider's final n km results table to " +
            " call this  method")
            raise ExpectedParsingError(error_msg)

        fields = parse_table_fields_args(args, available_fields)
        casual_fields = [f for f in fields
            if f not in ("vertical_meters", "average_percentage")]

        results_table_html = self.html.css_first("div:nth-child(4) table")
        table_parser = TableParser(results_table_html)
        table_parser.parse(casual_fields)
        # add vertical meters column if needed
        if "vertical_meters" in fields:
            vms = table_parser.parse_extra_column("Vertical meters", int)
            table_parser.extend_table("vertical_meters", vms)
        # add average percentages column if needed
        if "average_percentage" in fields:
            percentages = table_parser.parse_extra_column("Avg. %", float)
            table_parser.extend_table("average_percentage", percentages)
        return table_parser.table

    def seasons_select(self) -> List[Dict[str, str]]:
        """
        Parses seasons select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "xseason"))

    def races_select(self) -> List[Dict[str, str]]:
        """
        Parses race select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "race"))

    def pages_select(self) -> List[Dict[str, str]]:
        """
        Parses race select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "offset"))

    def stage_types_select(self) -> List[Dict[str, str]]:
        """
        Parses stage types select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "type"))

    def nations_select(self) -> List[Dict[str, str]]:
        """
        Parses nations select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "znation"))

    def categories_select(self) -> List[Dict[str, str]]:
        """
        Parses categories select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        return parse_select(select_menu_by_name(self.html, "category"))
