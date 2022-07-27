import datetime


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
