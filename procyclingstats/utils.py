import datetime
import math
import re
from typing import Any, Dict, List, Tuple, Union, Optional

from selectolax.parser import HTMLParser, Node

from .errors import ExpectedParsingError


# date and time manipulation functions
def get_day_month(str_with_date: str) -> str:
    """
    Gets day and month from string containing day/month or day-month.

    :param str_with_date: String with day and month separated by - or /.
    :raises ValueError: When string doesn't contain day and month in wanted
    format.
    :return: String in `MM-DD` format.
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

def convert_date(date: str) -> str:
    """
    Converts given date to `YYYY-MM-DD` format.

    :param date: Date to convert, day, month and year have to be separated by
    spaces and month has to be in word form e.g. `30 July 2022`.
    :return: Date in `YYYY-MM-DD` format.
    """
    [day, month, year] = date.split(" ")
    month = datetime.datetime.strptime(month, "%B").month
    month = f"0{month}" if month < 10 else str(month)
    return "-".join([year, month, day])

def timedelta_to_time(tdelta: datetime.timedelta) -> str:
    """
    Converts timedelta object to time in `H:MM:SS` format.

    :param tdelta: Timedelta to convert.
    :return: Formatted time.
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
    Converts time in `H:MM:SS` or `H:MM:SS.ms` format to timedelta.

    :param time: Time to convert.
    :return: Timedelta object.
    """
    try:
        # Split milliseconds if present
        if '.' in time:
            time_part, ms_part = time.split('.')
            milliseconds = int(ms_part.ljust(3, '0'))  # pad to ensure 3 digits
        else:
            time_part = time
            milliseconds = 0

        hours, minutes, seconds = [int(p) for p in time_part.split(":")]
        return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
    except Exception as e:
        raise ValueError(f"Invalid time format: {time}") from e

def format_time(time: str) -> str:
    """
    Convert time from formats like `M:SS`, `MM:SS`, or `MM.SS,ms` to `H:MM:SS` or `H:MM:SS.ms`.

    :param time: Time to convert.
    :return: Formatted time e.g. `31:03:11`.
    """
    # Handle European-style format: MM.SS,ms
    if ',' in time and '.' in time:
        time = time.replace(' ', '').replace(',', '.')
        parts = time.split('.')
        if len(parts) == 4:
            hours, minutes, seconds, hundredths = parts
        elif len(parts) == 3:
            hours = "0"
            minutes, seconds, hundredths = parts
        else:
            raise ValueError(f"Unexpected time format: {time}")
        return f"{int(hours)}:{minutes.zfill(2)}:{seconds.zfill(2)}.{hundredths}"
    
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
    together.

    :param time1: Time separated with colons.
    :param time2: Time separated with colons.
    :return: Time in `H:MM:SS` format.
    """
    tdelta1 = time_to_timedelta(format_time(time1))
    tdelta2 = time_to_timedelta(format_time(time2))
    tdelta = tdelta1 + tdelta2
    return timedelta_to_time(tdelta)

# HTML parsing functions
def parse_select(select_menu: Node) -> List[Dict[str, str]]:
    """
    Parses select menu.

    :param select_menu: Select menu HTML.
    :return: Parsed select menu represented as list of dicts with keys `text`
    and `value`.
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

    :param html: HTML to find select menu in.
    :param name_attr: Name attribute of wanted select menu.
    :raises ExpectedParsingError: When select menu with given name attribute
    isn't contained in given HTML.
    :return: Wanted select menu HTML.
    """
    select_html = html.css_first(f"select[name={name_attr}]")
    if not select_html:
        raise ExpectedParsingError(f"'{name_attr}' select not in page HTML.")
    return select_html


# other functions
def join_tables(table1: List[Dict[str, Any]],
               table2: List[Dict[str, Any]],
               join_key: str,
               skip_missing: bool = False) -> List[Dict[str, Any]]:
    """
    Join given tables to one by joining rows which `join_key` values are
    matching.

    :param table1: Table represented as list of dicts where every row has
    `join_key`.
    :param table2: Table represented as list of dicts where every row has
    `join_key`.
    :param join_key: Field used for finding matching rows, e.g. `rider_url`.
    :param skip_missing: If set to False, error is raised when table1 and
        table2 don't have same join_keys. Otherwise only rows with join_keys
        present in both tables are added.
    :return: Tables joined together into one table.
    """
    table2_dict = {row[join_key]: row for row in table2}
    table = []
    for row in table1:
        if not skip_missing or table2_dict.get(row[join_key]):
            table.append({**table2_dict[row[join_key]], **row})
    return table

def parse_table_fields_args(args: Tuple[str],
                            available_fields: Tuple[str, ...]) -> List[str]:
    """
    Check whether given args are valid and get table fields.

    :param args: Args to be validated.
    :param available_fields: Args that would be valid.
    :raises ValueError: When one of args is not valid.
    :return: Table fields, args if any were given, otherwise all available
    fields.
    """
    for arg in args:
        if arg not in available_fields:
            raise ValueError("Invalid field argument")
    if args:
        return list(args)
    return list(available_fields)

def get_height_weight(h: Optional[float], w: Optional[float]) -> Tuple[
                      Optional[float], Optional[float]]:
    """
    Based on expected human height and weight decides whether height and values have
    to be swapped.
    :param h: Height value
    :param w: Weight value.
    return: Tuple where first value is real height and second value is real weight.
    """
    weight, height = None, None
    # Case 1: Both values exist
    if w is not None and h is not None:
        weight = w if w >= 10 else h if h >= 10 else None
        height = h if h < 10 else w if w < 10 else None

    # Case 2: Only weight exists
    elif w is not None:
        weight = w if w >= 10 else None
        height = w if w < 10 else None

    # Case 3: Only height exists
    elif h is not None:
        height = h if h < 10 else None
        weight = h if h >= 10 else None

    # Post-validation for realistic ranges
    if weight and not (30 <= weight <= 120):
        weight = None
    if height and not (1.5 <= height <= 2.2):
        height = None
    return height, weight


