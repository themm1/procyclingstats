import datetime
import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from selectolax.parser import HTMLParser, Node

from .errors import ExpectedParsingError, ParsedValueInvalidError


class reg: # pylint: disable=invalid-name
    """
    Class for storing regex of common procyclingstats URL parts
    """
    base_url = "(https:\\/\\/www.procyclingstats.com\\/+)"
    """example match `https://www.procyclingstats.com/`"""
    url_str = "(\\/+([a-zA-Z]+-)*([a-zA-Z]+))"
    """example match `/This-is-url-StriNg`"""
    year = "(\\/+\\d{4})"
    """example match `/1111`"""
    stage = "(\\/+(((stage-([1-9]([0-9])?([a-z])?)|prologue)"\
            "(\\/gc|-points|-kom|-youth|-teams)?)|gc))"
    """example match `/stage-20/gc` or `/prologue-youth`"""
    result = "(\\/+result)"
    """example match `/result`"""
    overview = "(\\/+overview)"
    """example match `/overview`"""
    startlist = "(\\/+startlist)"
    """example match `/startlist`"""
    team_url_str = "(\\/(([a-zA-Z0-9]+-)+)\\d{4,5})"
    """example match `/bora-hansgrohe-2022` or `/movistar-team-20152`"""
    anything = "(\\/+.*)"
    """example match `/ffefwf//fwefw/aa`"""


# validation functions
def validate_string(string: str,
                    min_length: int = 0,
                    max_length: int = math.inf, # type: ignore
                    regex: str = "",
                    options: Optional[List[str]] = None,
                    can_be_none: bool = False,
                    error: Any = None) -> None:
    """
    Validates string based on given constraints

    :param string: string to be validated
    :param min_length: minimal string length, defaults to 0
    :param max_length: maximal string length, defaults to math.inf
    :param regex: regex that has to string full match, spaces and newlines are
    removed from given regex, defaults to ""
    :param can_be_none: whether string is valid when is None
    :param options: possible options that string could be, defaults to None
    :param error: constructed exception object to raise if string is not valid,
    when None raises ParsedValueInvalidError with given string
    :raises: given error when string is not valid
    """
    valid = True
    if not can_be_none and string is None:
        valid = False

    if options and string not in options:
        valid = False

    if len(string) < min_length or len(string) > max_length:
        valid = False

    if regex:
        if re.fullmatch(regex, string) is None:
            valid = False
    if not valid:
        if not error:
            raise ParsedValueInvalidError(string)
        else:
            raise error

def validate_number(number: Union[int, float],
                    min_: Union[int, float] = -math.inf,
                    max_: Union[int, float] = math.inf,
                    can_be_none: bool = False,
                    error: Any = None) -> None:
    """
    Validates number based on given constraints

    :param number: number to be validated
    :param min_: minimal value of number, defaults to -math.inf
    :param max_: maximal value of number, defaults to math.inf
    :param can_be_none: whether number is valid when is None
    :param error: constructed exception object to raise if number is not valid,
    when None raises ParsedValueInvalidError with given number
    :raises: given error when string is not valid
    """
    valid = True
    if not can_be_none and number is None:
        valid = False

    if number > max_ or number < min_:
        valid = False
    if not valid:
        if not error:
            raise ParsedValueInvalidError(number)
        else:
            raise error

# strings and URLs manipulation functions
def format_url_filter(url_filter: str) -> str:
    """
    Removes uneccessarry filters from URL filter string.

    :param url_filter: URL filter string
    :return: formatted URL filter
    """
    splitted_url = url_filter.split("?")
    if splitted_url[1] == "":
        return "rankings"
    if splitted_url[0] == "rankings":
        splitted_url[0] = "rankings.php"
    url_filter = splitted_url[1]
    filter_ = url_filter.split("&")
    formatted_url_filter = []
    for part in filter_:
        if part == "":
            continue
        [key, value] = part.split("=")
        if (key == "page" or value == "" or (key == "offset" and value == "0")
                or key == "filter"):
            continue
        formatted_url_filter.append(f"{key}={value}")
    formatted_filter = "&".join(formatted_url_filter)
    return f"{splitted_url[0]}?{formatted_filter}"

def normalize_race_url(decomposed_url: List[str], addon: str) -> str:
    """
    Creates normalized race URL.

    :param decomposed_url: list of URL strings
    :param addon: extra part added after race normalized URL
    :return: normalized URL in `race/{race_id}/{year}/{addon}` format
    """
    decomposed_url.extend([""] * (3 - len(decomposed_url)))
    race_id = decomposed_url[1]
    if decomposed_url[2].isnumeric() and len(decomposed_url[2]) == 4:
        year = decomposed_url[2]
    else:
        year = None
    normalized_url = f"race/{race_id}"
    if year is not None:
        normalized_url += f"/{year}/{addon}"
    else:
        normalized_url += f"/{addon}"
    return normalized_url

def format_regex_str(regex: str) -> str:
    """
    Formats given regex (removes newlines and spaces).

    :param regex: regex to format
    :return: regex without newlines and spaces
    """
    return "".join([char for char in regex if char not in ("\n", " ")])

def get_day_month(str_with_date: str) -> str:
    """
    Gets day and month from string containing day/month or day-month

    :param str_with_date: string with day and month separated by - or /
    :raises ValueError: if string doesn't contain day and month in wanted
    format
    :return: string in month-day format
    """
    day, month = "", ""
    # loop through string and check whether next 5 characters are in wanted
    # date format `day/month` or `day-month`
    for i, _ in enumerate(str_with_date[:-4]):
        if str_with_date[i:i + 2].isnumeric() and \
                str_with_date[i + 3:i + 5].isnumeric():
            if str_with_date[i + 2] == "/":
                [day, month] = str_with_date[i:i + 5].split("/")
            elif str_with_date[i + 2] == "-":
                [day, month] = str_with_date[i:i + 5].split("-")
    if day.isnumeric() and month.isnumeric():
        return f"{month}-{day}"
    # day or month weren't numeric so given string doesn't contain date in
    # wanted format
    raise ValueError(
        "Given string doesn't contain day and month in wanted format")


# date and time manipulation functions
def convert_date(date: str) -> str:
    """
    Converts given date to `YYYY-MM-DD` format

    :param date: date to convert, day, month and year have to be separated by
    spaces and month has to be in word form e.g. `30 July 2022`
    :return: date in `YYYY-MM-DD` format
    """
    [day, month, year] = date.split(" ")
    month = datetime.datetime.strptime(month, "%B").month
    month = f"0{month}" if month < 10 else str(month)
    return "-".join([year, month, day])

def timedelta_to_time(tdelta: datetime.timedelta) -> str:
    """
    Converts timedelta object to time in `H:MM:SS` format

    :param tdelta: timedelta to convert
    :return: time
    """
    time = str(tdelta).split(" ")
    if len(time) > 1:
        days = time[0]
        time = time[2]
        hours = int(time.split(":")[0]) + (24 * int(days))
        minutes_seconds = ":".join(time.split(":")[1:])
    else:
        hours = time[0].split(":")[0]
        minutes_seconds = ":".join(time[0].split(":")[1:])
    return f"{hours}:{minutes_seconds}"

def time_to_timedelta(time: str) -> datetime.timedelta:
    """
    Converts time in `H:MM:SS` format to timedelta object

    :param time: time to convert
    :return: timedelta object
    """
    [hours, minutes, seconds] = [int(value) for value in time.split(":")]
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

def format_time(time: str) -> str:
    """
    Convert time from `M:SS` or `MM:SS` format to `H:MM:SS` format

    :param time: time to convert
    :return: formatted time e.g. `31:03:11`
    """
    splitted_time = time.split(":")
    # make minutes and seconds two digits long
    for i, time_val in enumerate(splitted_time [-2:]):
        if len(time_val) == 1:
            splitted_time[i] = "0" + time_val
    time_str = ":".join(splitted_time)
    # add hours if needed
    if len(splitted_time) == 2:
        time_str = "0:" + time_str
    return time_str

def add_times(time1: str, time2: str) -> str:
    """
    Adds two given times with minutes and seconds or with hours optionally
    together

    :param time1: time separated with colons
    :param time2: time separated with colons
    :return: time in `H:MM:SS` format
    """
    tdelta1 = time_to_timedelta(format_time(time1))
    tdelta2 = time_to_timedelta(format_time(time2))
    tdelta = tdelta1 + tdelta2
    return timedelta_to_time(tdelta)

# HTML parsing functions
def parse_select(select_menu: Node) -> List[Dict[str, str]]:
    """
    Parses select menu.

    :param select_menu: select menu HTML
    :return: parsed select menu represented as list of dicts with keys 'text'
    and 'value'
    """
    table = []
    for option in select_menu.css("option"):
        table.append({
            "text": option.text(),
            "value": option.attributes['value']
        })
    return table

def select_menu_by_name(html: Union[Node, HTMLParser], name_attr: str) -> Node:
    """
    Finds select menu my it's name attribute.

    :param html: HTML to find select menu in
    :param name_attr: name attribute of wanted select menu
    :raises ExpectedParsingError: when select menu with given name attribute
    isn't contained in given HTML
    :return: wanted select menu HTML
    """
    select_html = html.css_first(f"select[name={name_attr}]")
    if not select_html:
        raise ExpectedParsingError(f"'{name_attr}' select not in page HTML.")
    return select_html


# other functions
def join_tables(table1: List[Dict[str, Any]],
               table2: List[Dict[str, Any]] ,
               join_key: str) -> List[Dict[str, Any]]:
    """
    Join given tables to one by joining rows which `join_key` values are
    matching.

    :param table1: table represented as list of dicts where every row has
    `join_key`
    :param table2: table represented as list of dicts where every row has
    `join_key`
    :param join_key: field used for finding matching rows, e.g. `rider_url`
    :return: tables joined together into one table
    """
    table2_dict = {row[join_key]: row for row in table2}
    table = []
    for row in table1:
        table.append({**table2_dict[row[join_key]], **row})
    return table

def parse_table_fields_args(args: Tuple[str],
                            available_fields: Tuple[str]) -> List[str]:
    """
    Check whether given args are valid and get table fields

    :param args: args to be validated
    :param available_fields: args that would be valid
    :raises ValueError: when one of args is not valid
    :return: table fields, args if any were given, otherwise all available\
        fields
    """
    for arg in args:
        if arg not in available_fields:
            raise ValueError("Invalid field argument")
    if args:
        return list(args)
    else:
        return list(available_fields)
