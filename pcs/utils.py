import os
import csv
import json
import datetime
import warnings
from pprint import pprint
from typing import Dict, Any, Literal
from requests_html import HTMLSession, HTML

class RequestWrapper:
    """
    Base class used for making requests to `https://www.procyclingstats.com/`

    Usage of subclasses:
        Use `self.update_html` to make request to `self.url` and update\
            `self.html`, `self.parse_html` parses all information from site and\
            updates `self.content`. Other methods are used by `self.parse_html`\
            and are used to get concrete information e.g. from Rider class\
            `birthdate` method returns rider's birthdate

    Attributes:
        base_url: `https://www.procyclingstats.com/`, URL to be omitted when
            passing url parameter
        html: HTML to be parsed from, empty requests_html.HTML object on default
        url: URL to get HTML from using `update_html`
        print_request_url: whether to print URL of request when making request

    Args:
        print_request_url: whether to print URL of request when making request
    """
    base_url: Literal["https://www.procyclingstats.com/"] = \
        "https://www.procyclingstats.com/"
    def __init__(self, url: str, print_request_url: bool=True) -> None:
        # .html and .url are going to be overridden by subclasses
        self.url: str = url
        self.print_request_url: bool = print_request_url
        self.html: HTML = HTML(html="<HTML>")
        self.content: Dict[str, Any] = {}

    def __repr__(self) -> str:
        """:returns: relative `self.url` (without `self.base_url`)"""
        if "https" in self.url:
            return self.url.split("/")[1:]
        return self.url
    
    def _request_html(self, url: str) -> HTML:
        """
        Makes request to given url and returns it's HTML, if given url isn't\
            valid raises ValueError
        :param url: URL to get HTML from base_url
        :returns: HTML obtained from given URL
        """
        session = HTMLSession()
        url = self.base_url + url if "https://" not in url else url
        if self.print_request_url:
            print(url)
        html = session.get(url).html
        if html.find(".page-title > .main > h1")[0].text == "Page not found":
            raise ValueError(f"Invalid URL: {url}")
        return html

    def update_html(self) -> None:
        """
        Calls request to `url` using `RequestWrapper._request_html` and
        updates `self.html` to returned HTML
        """
        self.html = self._request_html(self.url)
        
    def parse_html(self) -> None:
        """Empty method that is going to be overridden by subclasses"""
        pass

    def build(self) -> Dict[str, Any]:
        """
        Calls `self.update_html` and `self.parse_html`
        :returns: `self.content` dict with all parsable info from page
        """
        self.update_html()
        return self.parse_html()


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
        minutes=int(t2minutes), seconds=int(t2seconds))
    if " day, " in str(time_b):
        [days, time] = str(time_b).split(" day, ")
    elif " days, " in str(time_b):
        [days, time] = str(time_b).split(" days, ")
    else:
        days = 0
        time = str(time_b)
    return f"{days} {time}"