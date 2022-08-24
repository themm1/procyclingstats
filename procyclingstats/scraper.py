import inspect
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import requests
from selectolax.parser import HTMLParser

from .errors import ExpectedParsingError, ParsedValueInvalidError
from .utils import validate_string


class Scraper:
    """
    Used as base class for scraping classes.

    :param url: URL of race overview either full or relative, e.g.
    `race/tour-de-france/2021/stage-8`
    :param html: HTML to be parsed from, defaults to None, when passing the
    parameter, set `update_html` to False to prevent overriding or making
    useless request
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to make object ready for parsing, defaults to True
    """
    BASE_URL: Literal["https://www.procyclingstats.com/"] = \
        "https://www.procyclingstats.com/"
    _public_nonparsing_methods = (
        "update_html",
        "parse",
        "relative_url"
    )
    """Public methods that aren't called by `parse` method."""
    _url_validation_regex = ".*"
    """Regex for validating URL. Should be overridden by subclass."""

    def __init__(self, url: str, html: Optional[str] = None,
                 update_html: bool = True) -> None:
        self._validate_url(url)
        self._url = self._make_url_absolute(url)
        self._html = None
        if html:
            self._html = HTMLParser(html)
        if update_html:
            self.update_html()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(url='{self.normalized_relative_url()}')"

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.normalized_relative_url() == other.normalized_relative_url()

    @property
    def url(self) -> str:
        """Get URL of a scraper object"""
        return self._url

    @property
    def html(self) -> HTMLParser:
        """
        Get HTML of a scraper object

        :raises ExpectedParsingError: when HTML is None
        """
        if self._html is None:
            raise ExpectedParsingError(
                "In order to access HTML, update it using `self.update_html` " +
                "method")
        return self._html

    def relative_url(self) -> str:
        """
        Makes relative URL from absolute url (cuts `self.BASE_URL` from URL)

        :return: relative URL
        """
        return "/".join(self._url.split("/")[3:])

    def normalized_relative_url(self) -> str:
        """
        Creates normalized relative URL. By default only removes extra slashes
        from user defined relative URL. Is used for evaluating equality of
        objects and should be overridden by subclass.

        :return: normalized URL
        """
        return "/".join(self._decompose_url())

    def update_html(self) -> None:
        """
        Calls request to `self.url` using `Scraper._request_html` and
        updates `self.html` to returned HTML
        :raises ValueError: when URL isn't valid (after making request)
        """
        html_str = self._request_html()
        html = HTMLParser(html_str)
        if html.css_first(".page-title > .main > h1").text()== "Page not found":
            raise ValueError(f"Invalid URL: {self._url}")
        self._html = html

    def parse(self,
              exceptions_to_ignore: Tuple[Any, ...] = (ExpectedParsingError,),
              none_when_unavailable: bool = True) -> Dict[str, Any]:
        """
        Creates JSON like dict with parsed data by calling all parsing methods.
        Keys in dict are methods names and values parsed data

        :param exceptions_to_ignore: tuple of exceptions that should be ignored,
        defaults to `(ExpectedParsingError)`
        :param none_when_unavailable: whether to set dict value to None when
        method raises ignored exception
        :return: dict with parsing methods mapping to parsed data
        """
        parsing_methods = self._parsing_methods()
        parsed_data = {}
        for method_name, method in parsing_methods:
            try:
                parsed_data[method_name] = method()
            except exceptions_to_ignore:
                if none_when_unavailable:
                    parsed_data[method_name] = None
        return parsed_data

    def _decompose_url(self) -> List[str]:
        """
        Splits relative URL to list of strings.

        :return: splitted relative URL without empty strings
        """
        splitted_url = self.relative_url().split("/")
        return [part for part in splitted_url if part]

    def _validate_url(self, url: str) -> None:
        """
        Validates given URL with regex and returns absolute URL.

        :param url: URL either relative or absolute
        :raises ValueError: when URL isn't valid
        :return: valid absolute URL
        """
        try:
            validate_string(url, regex=self._url_validation_regex)
        except ParsedValueInvalidError:
            raise ValueError(f"Given URL is indvalid: '{url}'")

    def _parsing_methods(self) -> List[Tuple[str, Callable]]:
        """
        Gets all parsing methods from a class. That are all public methods
        except of methods listed in `_public_nonparsing_methods`.

        :return: list of tuples parsing methods names and parsing methods
        """
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        parsing_methods = []
        for method_name, method in methods:
            if (method_name[0] != "_"
                and method_name not in Scraper._public_nonparsing_methods):
                parsing_methods.append((method_name, method))
        return parsing_methods

    def _make_url_absolute(self, url: str) -> str:
        """
        Makes absolute URL from given url (adds `self.base_url` to URL if
        needed)

        :param url: URL to format
        :return: absolute URL
        """
        if "https" not in url:
            if url[0] == "/":
                url = self.BASE_URL + url[1:]
            else:
                url = self.BASE_URL + url
        return url

    def _request_html(self) -> str:
        """
        Makes request to `self.url` and returns it's HTML

        :return: HTML obtained from `self.url` as str
        """
        return requests.get(self._url).text
