from typing import Any, Dict, List, Tuple

from selectolax.parser import HTMLParser

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import (format_regex_str, format_url_filter, parse_select,
                    parse_table_fields_args, reg, select_menu_by_name)


class RiderResults(Scraper):
    """
    Scraper for rider results HTML page. Example URL:
    `rider/tadej-pogacar/results`. Supported is besides of default results table
    also final 5k results table which can be parsed using
    `self.final_n_km_results` method.
    """
    _url_validation_regex = format_regex_str(
    f"""
        {reg.base_url}?
        (rider.php\\?.*
        \\/*
        |
        rider
        {reg.url_str}\\/*results{reg.anything}?
        \\/*)
    """)
    """Regex for validating rider results URL."""

    @staticmethod
    def _html_invalid(html: HTMLParser) -> bool:
        """
        Overrides `Scraper` method.

        :param html: HTML to validate
        :return: True if given HTML is invalid, otherwise False
        """
        page_title = html.css_first(".page-content > h2").text()
        return (page_title != "All results" and
                page_title != "Top results final 5k analysis")

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. Determines equality of objects (is
        used in __eq__ method). Rider results objects are equal when both have
        same URL or filter values are the same (empty filter values don't
        count).

        :return: normalized filter URL or URL in `rider/{rider_id}/results'
        format
        """
        relative_url = self.relative_url()
        if "?" in relative_url:
            return format_url_filter(relative_url)
        decomposed_url = self._decompose_url()
        rider_id = decomposed_url[1]
        if (len(decomposed_url) >= 4 and
                decomposed_url[3] == "final-5k-analysis"):
            return f"rider/{rider_id}/results/final-5k-analysis"
        return f"rider/{rider_id}/results"

    def _set_up_html(self):
        """Overrides Scraper method. Removes last table row with sum stats."""
        results_table_html = self.html.css_first("table")
        for row in results_table_html.css("tr"):
            if "class" in row.attributes and row.attributes['class'] == "sum":
                row.decompose()

    def results(self, *args: str, available_fields: Tuple[str, ...] = (
            "date",
            "rank",
            "stage_url",
            "stage_name",
            "class",
            "distance",
            "pcs_points",
            "uci_points"
        )) -> List[Dict[str, Any]]:
        """
        Parses rider's results table from HTML. 
        
        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises ExpecterParsingError: when general results table is not
        contained in the HTML
        :return: rider's results table represented as list of dicts
        """
        if self.html.css_first(".page-content > h2").text() != "All results":
            error_msg = ("This object doesn't support 'results' method. " +
                "Create one from rider's default results table to call this " +
                "method")
            raise ExpectedParsingError(error_msg)

        fields = parse_table_fields_args(args, available_fields)
        results_table_html = self.html.css_first("table")
        tp = TableParser(results_table_html)
        tp.parse(fields)
        return tp.table

    def final_n_km_results(self, *args: str,
                           available_fields: Tuple[str, ...] = (
                                "date",
                                "rank",
                                "stage_url",
                                "stage_name",
                                "class",
                                "vertical_meters",
                                "average_percentage"
                           )) -> List[Dict[str, Any]]:
        """
        Parses rider's final N kms results table from HTML. 
        
        :param *args: fields that should be contained in results table
        :param available_fields: default fields, all available options
        :raises ValueError: when one of args is invalid
        :raises ExpecterParsingError: when final n kms results table is not
        contained in the HTML
        :return: results table represented as list of dicts
        """
        if (self.html.css_first(".page-content > h2").text() !=
                "Top results final 5k analysis"):
            error_msg = ("This object doesn't support 'final_n_km_results'" +
            "method. Create one from rider's final n km results table to call" +
            "this  method")
            raise ExpectedParsingError(error_msg)

        fields = parse_table_fields_args(args, available_fields)
        casual_fields = [f for f in fields
            if f not in ("vertical_meters", "average_percentage")]
        
        results_table_html = self.html.css_first("table")
        tp = TableParser(results_table_html)
        tp.parse(casual_fields)
        # add vertical meters column if needed
        if "vertical_meters" in fields:
            vms = tp.parse_extra_column("Vertical meters", int)
            tp.extend_table("vertical_meters", vms)
        # add average percentages column if needed
        if "average_percentage" in fields:
            percentages = tp.parse_extra_column("Avg. %", float)
            tp.extend_table("average_percentage", percentages)
        return tp.table

    def seasons_select(self) -> List[Dict[str, str]]:
        """
        Parses seasons select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        return parse_select(select_menu_by_name(self.html, "xseason"))

    def races_select(self) -> List[Dict[str, str]]:
        """
        Parses race select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        return parse_select(select_menu_by_name(self.html, "race"))

    def pages_select(self) -> List[Dict[str, str]]:
        """
        Parses race select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        return parse_select(select_menu_by_name(self.html, "offset"))

    def stage_types_select(self) -> List[Dict[str, str]]:
        """
        Parses stage types select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        return parse_select(select_menu_by_name(self.html, "type"))

    def nations_select(self) -> List[Dict[str, str]]:
        """
        Parses nations select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        return parse_select(select_menu_by_name(self.html, "znation"))

    def categories_select(self) -> List[Dict[str, str]]:
        """
        Parses categories select menu from HTML.

        :return: parsed select menu represented as list of dicts with keys
        'text' and 'value'
        """
        return parse_select(select_menu_by_name(self.html, "category"))
