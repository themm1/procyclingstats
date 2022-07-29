import datetime


def parse_table_fields_args(args: tuple, available_fields: tuple) -> tuple:
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
        return args
    else:
        return available_fields


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
