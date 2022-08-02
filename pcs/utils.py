import datetime
from typing import List, Tuple

from requests_html import HTML


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


course_translator = {
    "p0": (None, None),
    "p1": ("flat", 0),
    "p2": ("hilly", 0),
    "p3": ("hilly", 1),
    "p4": ("mountain", 0),
    "p5": ("mountain", 1),
}
