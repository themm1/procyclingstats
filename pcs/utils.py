import datetime
from typing import Dict, Any, Literal
from requests_html import HTMLSession, HTML


class RequestWrapper:
    base_url: Literal["https://www.procyclingstats.com/"] = \
        "https://www.procyclingstats.com/"

    def __init__(self, url: str, print_request_url: bool = False) -> None:
        """
        Used as base class for scraping classes

        :param url: URL to be parsed from
        :param print_request_url: whether to print URL when making request,\
            defaults to True
        """
        # .html and .url are going to be overridden by subclasses
        self.url: str = self._format_url(url)
        self.print_request_url: bool = print_request_url
        self.html: HTML = self._request_html()
        self.content: Dict[str, Any] = {}

    def __repr__(self) -> str:
        """:return: `self.url`"""
        return self.url

    def _format_url(self, url: str) -> str:
        """
        Makes full URL from given url (adds `self.base_url` to URL if needed)

        :param url: URL to format
        :return: full URL
        """
        if "https" not in url:
            if url[-1] == "/":
                url = self.base_url + url[:-1]
            else:
                url = self.base_url + url
        return url

    def _cut_base_url(self) -> str:
        """
        Makes relative URL from absolute url (cuts `self.base_url` from URL)

        :return: relative URL
        """
        return "/".join(self.url.split("/")[3:])

    def _request_html(self) -> HTML:
        """
        Makes request to `self.url` and returns it's HTML

        :raises ValueError: if URL isn't valid (after making request)
        :return: HTML obtained from `self.url`
        """
        session = HTMLSession()
        if self.print_request_url:
            print(self.url)
        html = session.get(self.url).html
        if html.find(".page-title > .main > h1")[0].text == "Page not found":
            raise ValueError(f"Invalid URL: {self.url}")
        return html

    def update_html(self) -> None:
        """
        Calls request to `self.url` using `RequestWrapper._request_html` and
        updates `self.html` to returned HTML
        """
        self.html = self._request_html()


def convert_date(date: str) -> str:
    [day, month, year] = date.split(" ")
    month = datetime.datetime.strptime(month, "%B").month
    month = f"0{month}" if month < 10 else str(month)
    return "-".join([year, month, day])


def format_time(time: str):
    time_length = len(time.split(":"))
    for _ in range(3-time_length):
        time = "".join(["00:", time])
    return time


def add_time(time1: str, time2: str) -> str:
    [t1hours, t1minutes, t1seconds] = format_time(time1).split(":")
    [t2hours, t2minutes, t2seconds] = format_time(time2).split(":")
    time_a = datetime.timedelta(hours=int(t1hours), minutes=int(t1minutes),
                                seconds=int(t1seconds))
    time_b = time_a + datetime.timedelta(hours=int(t2hours),
                                         minutes=int(t2minutes),
                                         seconds=int(t2seconds))
    if " day, " in str(time_b):
        [days, time] = str(time_b).split(" day, ")
    elif " days, " in str(time_b):
        [days, time] = str(time_b).split(" days, ")
    else:
        days = 0
        time = str(time_b)
    return f"{days} {time}"
