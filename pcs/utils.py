import datetime
import math
import re
from typing import List, Optional, Tuple, Union

from requests_html import HTML


class reg:
    """
    Class for storing regex of common procyclingstats URL parts
    """
    base_url = "(https:\\/\\/www.procyclingstats.com\\/+)"
    """example match `https://www.procyclingstats.com/`"""
    url_str = "(\\/+([a-zA-Z]+-)*([a-zA-Z]+))"
    """example match `/This-is-url-StriNg`"""
    year = "(\\/+\\d{4})"
    """example match `/1111`"""
    stage = "(\\/+(((stage-(1[0-9]|2[0-1]|[0-9])|prologue)"\
            "(\\/gc|-points|-kom|-youth|-teams)?)|gc))"
    """example match `/stage-20/gc` or `/prologue-youth`"""
    result = "((\\/+result){1,2})"
    """example match `/result/result`"""
    overview = "((\\/+overview){1,3})"
    """example match `/overview/overview`"""
    team_url_str = "(\\/(([a-zA-Z]+-)+)\\d{4,5})"
    """example match `/bora-hansgrohe-2022` or `/movistar-team-20152`"""
    rankings_filter = "(rankings[^\\?]*\\?.*)"
    """example match `rankingsfffff?rgrr`"""


def validate_string(string: str,
                    min_length: int = 0,
                    max_length: int = math.inf,
                    regex: str = "",
                    options: Optional[List[str]] = None,
                    can_be_none: bool = False) -> None:
    """
    Validates string based on given constraints

    :param string: string to be validated
    :param min_length: minimal string length, defaults to 0
    :param max_length: maximal string length, defaults to math.inf
    :param regex: regex that has to string full match, spaces and newlines are
    removed from given regex, defaults to ""
    :param can_be_none: whether string is valid when is None
    :param options: possible options that string could be, defaults to None
    """
    if not can_be_none and string is None:
        raise ValueError()

    if options and string not in options:
        raise ValueError()

    if len(string) < min_length or len(string) > max_length:
        raise ValueError()

    if regex:
        regex = [char for char in regex if char not in ("\n", " ")]
        formatted_regex = "".join(regex)
        if re.fullmatch(formatted_regex, string) is None:
            raise ValueError()


def validate_number(number: Union[int, float],
                    min_: Union[int, float] = -math.inf,
                    max_: Union[int, float] = math.inf,
                    can_be_none: bool = False) -> None:
    """
    Validates number based on given constraints

    :param number: number to be validated
    :param min_: minimal value of number, defaults to -math.inf
    :param max_: maximal value of number, defaults to math.inf
    :param can_be_none: whether number is valid when is None
    :raises ValueError: when number isn't valid
    """
    if not can_be_none and number is None:
        raise ValueError()

    if number > max_ or number < min_:
        raise ValueError()


def get_day_month(str_with_date: str) -> Tuple[str, str]:
    """
    Gets day and month from string containing day/month or day-month

    :param str_with_date: string with day and month separated by - or /
    :raises ValueError: if string doesn't contain day and month in wanted
    format
    :return: tuple in (day, month) format where day and month are numeric
    strings
    """
    day, month = "", ""
    # loop through string and check whether next 5 characters are in wanted
    # date format `day/month` or `day-month`
    for i, char in enumerate(str_with_date[:-4]):
        if str_with_date[i:i + 2].isnumeric() and \
                str_with_date[i + 3:i + 5].isnumeric():
            if str_with_date[i + 2] == "/":
                [day, month] = str_with_date[i:i + 5].split("/")
            elif str_with_date[i + 2] == "-":
                [day, month] = str_with_date[i:i + 5].split("-")
    if day.isnumeric() and month.isnumeric():
        return day, month
    # day or month weren't numeric so given string doesn't contain date in
    # wanted format
    raise ValueError(
        "Given string doesn't contain day and month in wanted format")


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


def parse_select_menu(select_html: HTML) -> List[dict]:
    """
    Parses given HTML select menu

    :param select_html: HTML select menu to be parsed
    :return: list of dicts where `value` is value of item from select menu
    and `text` is text of the item from select menu
    """
    parsed_select = []
    for option in select_html.find("option"):
        parsed_select.append({
            "value": option.attrs['value'],
            "text": option.text
        })
    return parsed_select


def convert_date(date: str) -> str:
    [day, month, year] = date.split(" ")
    month = datetime.datetime.strptime(month, "%B").month
    month = f"0{month}" if month < 10 else str(month)
    return "-".join([year, month, day])


def format_time(time: str):
    time_length = len(time.split(":"))
    for _ in range(3 - time_length):
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
