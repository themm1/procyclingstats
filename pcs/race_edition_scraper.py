from typing import List, Optional, Tuple

from .errors import ExpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import parse_table_fields_args, reg


class RaceEdition(Scraper):
    """
    Scraper for race overview page.

    :param url: URL of race overview either full or relative, e.g.
    `race/tour-de-france/2021/overview`
    :param html: HTML to be parsed from, defaults to None, when passing the
    parameter, set `update_html` to False to prevent overriding or making
    useless request
    :param update_html: whether to make request to given URL and update
    `self.html`, when False `self.update_html` method has to be called
    manually to set HTML (when isn't passed), defaults to True
    """

    def __init__(self, url: str, html: Optional[str] = None,
                 update_html: bool = True) -> None:
        super().__init__(url, html, update_html)

    def _get_valid_url(self, url: str) -> str:
        """
        Validates given URL with regex and returns absolute URL

        :param url: URL either relative or absolute
        :raises ValueError: when URL isn't valid
        :return: absolute URL
        """
        race_url_overview_regex = f"""
            {reg.base_url}?race{reg.url_str}
            ({reg.year}{reg.stage}{reg.overview}|{reg.year}{reg.overview})
            (\\/+)?
        """
        self._validate_url(url, race_url_overview_regex,
                           "race/tour-de-france/2021/overview")
        return self._make_absolute_url(url)

    def year(self) -> int:
        """
        Parse year when the race occured

        :return: year
        """
        return int(self._html.find("span.hideIfMobile")[0].text)

    def display_name(self) -> str:
        """
        Parses display name from HTML

        :return: display name e.g. `Tour de France`
        """
        display_name_html = self._html.find(".page-title > .main > h1")[0]
        return display_name_html.text

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is one day race from HTML

        :return: whether given race is one day race
        """
        one_day_race_html = self._html.find("div.sub > span.blue")[0]
        return "stage" not in one_day_race_html.text.lower()

    def nationality(self) -> str:
        """
        Parses race nationality from HTML

        :return: 2 chars long country code
        """
        nationality_html = self._html.find(".page-title > .main > span")[0]
        return nationality_html.attrs['class'][1].upper()

    def edition(self) -> int:
        """
        Parses race edition year from HTML

        :return: edition as int
        """
        edition_html_list = self._html.find(".page-title > .main > span + font")
        if edition_html_list:
            return int(edition_html_list[0].text[:-2])
        raise ExpectedParsingError("Race cancelled, edition unavailable.")

    def startdate(self) -> str:
        """
        Parses race startdate from HTML

        :return: startdate in `DD-MM-YYYY` format
        """
        startdate_html = self._html.find(".infolist > li > div:nth-child(2)")[0]
        return startdate_html.text

    def enddate(self) -> str:
        """
        Parses race enddate from HTML

        :return: enddate in `DD-MM-YYYY` format
        """
        enddate_html = self._html.find(".infolist > li > div:nth-child(2)")[1]
        return enddate_html.text

    def category(self) -> str:
        """
        Parses race category from HTML

        :return: race category e.g. `Men Elite`
        """
        category_html = self._html.find(".infolist > li > div:nth-child(2)")[2]
        return category_html.text

    def uci_tour(self) -> str:
        """
        Parses UCI Tour of the race from HTML

        :return: UCI Tour of the race e.g. `UCI Worldtour`
        """
        uci_tour_html = self._html.find(".infolist > li > div:nth-child(2)")[3]
        return uci_tour_html.text

    def stages(self, *args: str, available_fields: Tuple[str, ...] = (
            "date",
            "profile_icon",
            "stage_name",
            "stage_url",
            "distance")) -> List[dict]:
        """
        Parses race stages from HTML (available only on stage races)

        :param *args: fields that should be contained in results table,
        available options are a all included in `fields` default value
        :param available_fields: default fields, all available options
        :raises Exception: when race is one day race
        :return: table with wanted fields represented as list of dicts
        """
        if self.is_one_day_race():
            raise ExpectedParsingError(
                "This method is available only on stage races")
        fields = parse_table_fields_args(args, available_fields)

        stages_fields = [field for field in fields if field != "date"]
        stages_table_html = self._html.find("div:nth-child(3) > ul.list")[0]
        tp = TableParser(stages_table_html)
        # function to skip rest days when parsing table
        def skip_func(x): return True if "Restday" in x.text else False
        tp.parse(stages_fields, skip_func)
        if "date" in fields:
            tp.extend_table("date", 0, self._day_month_to_date, skip_func)
        return tp.table

    def _day_month_to_date(self, day_month) -> str:
        """
        Convert day and month e.g. `30/7` to date with race year

        :param day_month: day and month separated by '/'
        :return: date in in `YYYY-MM-DD` format
        """
        [day, month] = day_month.split("/")
        return f"{self.year()}-{month}-{day}"
