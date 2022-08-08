from typing import Any, Dict, Literal, Optional, Union

from requests_html import HTML, HTMLSession

from utils import validate_string


class Scraper:
    """
    Used as base class for scraping classes

    :param url: URL to be parsed from
    :param update_html: whether to make request to given URL and update
    object's HTML, when False `self.update_html` method has to be called
    manually to make object ready for parsing
    """
    BASE_URL: Literal["https://www.procyclingstats.com/"] = \
        "https://www.procyclingstats.com/"

    def __init__(self, url: str, html: Optional[str],
                 update_html: bool) -> None:
        self._url: str = self._get_valid_url(url)
        self._html: Optional[HTML] = None
        if html:
            self._html = self._get_valid_html(html)
        if update_html:
            self.update_html()

    def __repr__(self) -> str:
        """Returns `self.url`"""
        return self._url

    @property
    def url(self) -> str:
        """Get URL of a scraper object"""
        return self._url

    @property
    def html(self) -> HTML:
        """Get HTML of a scraper object"""
        return self._html

    def _get_valid_html(self, html: str) -> HTML:
        try:
            return HTML(html=html, url=self._url)
        except TypeError:
            raise TypeError("HTML has to be a string")

    def _get_valid_url(self, url: str) -> str:
        """
        Method for validating and formatting given URL, should be overriden by
        subclass

        :return: absolute URL
        """
        return self._make_absolute_url(url)

    def _make_absolute_url(self, url: str) -> str:
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

    def _validate_url(
            self,
            url: str,
            url_regex: str,
            correct_url_example: str):
        """
        Validates URL with given regex

        :param url: URL to be validated
        :param url_regex: regex that has to fullmatch with given URL
        :param correct_url_example: example to print when ValueError is raised
        :raises ValueError: when URL is invalid
        """
        try:
            validate_string(url, regex=url_regex)
        except ValueError:
            raise ValueError(f"Given URL is indvalid: '{url}', example of valid"
                             f" URL: '{correct_url_example}'")

    def relative_url(self) -> str:
        """
        Makes relative URL from absolute url (cuts `self.base_url` from URL)

        :return: relative URL
        """
        return "/".join(self._url.split("/")[3:])

    def _request_html(self) -> HTML:
        """
        Makes request to `self.url` and returns it's HTML

        :raises ValueError: when URL isn't valid (after making request)
        :return: HTML obtained from `self.url`
        """
        session = HTMLSession()
        html = session.get(self._url).html
        if html.find(".page-title > .main > h1")[0].text == "Page not found":
            raise ValueError(f"Invalid URL: {self._url}")
        return html

    def update_html(self) -> None:
        """
        Calls request to `self.url` using `Scraper._request_html` and
        updates `self.html` to returned HTML
        :raises ValueError: when URL isn't valid (after making request)
        """
        self._html = self._request_html()
