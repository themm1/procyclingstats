from typing import Any, Dict, List

from .scraper import Scraper
from .utils import (format_regex_str, format_url_filter, parse_select,
                    parse_table_fields_args, reg)


class RiderResults(Scraper):
    """
    Scraper for rider results HTML page. Example URL:
    `rider/tadej-pogacar/results`
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
        return f"rider/{rider_id}/results"



