from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from selectolax.parser import Node

from .errors import ExpectedParsingError, UnexpectedParsingError
from .utils import add_times, format_time


class TableParser:
    """
    Parser for HTML tables. Parsed content is stored in `self.table`, which is
    represented as list of dicts.

    :param html_table: HTML table to be parsed from
    """

    table_row_dict: Dict[str, str] = {
        "tbody": "tr",
        "table": "tr",
        "ul": "li"
    }
    """Finds out what is the table row tag"""
    row_column_tag_dict: Dict[str, str] = {
        "tr": "td",
        "li": "div"
    }
    """Finds out what is the table row column tag"""

    def __init__(self, html_table: Node) -> None:
        self.table = []
        table_body = html_table.css_first("tbody")
        if table_body:
            self.html_table = table_body
            self.header = html_table.css_first("thead")
        else:
            self.html_table = html_table
            self.header = None

        self.table_row_tag = self.table_row_dict[self.html_table.tag]
        self.row_column_tag = self.row_column_tag_dict[self.table_row_tag]

        self.a_elements = self.html_table.css("a")
        self.table_length = len(self.html_table.css(self.table_row_tag))
        self.row_length = len(self.html_table.css(
            f"{self.table_row_tag}:first-child > {self.row_column_tag}"))

    def parse(self, fields: Union[List[str], Tuple[str, ...]]) -> None:
        """
        Parses HTML table to `self.table` (list of dicts) by calling given
        table parsing methods. Every parsed table row is dictionary with
        `fields` keys

        :param fields: table parsing methods of this class
        :raises UnexpectedParsingError: when parsed field values aren't the
        same size as table length

        :regular fields options:
            - rider_url
            - rider_name
            - team_url
            - team_name
            - stage_url
            - stage_name
            - nation_url
            - nation_name
            - age
            - nationality
            - time
            - bonus
            - profile_icon
            - season

        :fields options for tables with a header:
            - rank
            - status
            - prev_rank
            - pcs_points
            - uci_points
            - points
            - class
            - first_places
            - second_places
            - third_places
            - distance
            - date
        """
        raw_table = []
        for _ in range(self.table_length):
            raw_table.append({})

        for field in fields:
            if field != "class":
                parsed_field_list = getattr(self, field)()
            # special case when field is called class
            else:
                parsed_field_list = getattr(self, "class_")()
            # field wasn't found in every table row, so isn't matching table
            # rows correctly
            if len(parsed_field_list) != self.table_length:
                message = f"Field '{field}' wasn't parsed correctly"
                raise UnexpectedParsingError(message)

            for row, parsed_value in zip(raw_table, parsed_field_list):
                row[field] = parsed_value

        # remove unwanted rows
        for row in raw_table:
            self.table.append(row)

        if "time" in fields and self.table:
            self._make_times_absolute()

    def extend_table(self, field_name: str, values: List[Any]):
        """
        Add given values to table.

        :param field_name: name for column that's being added
        :param values: values which are being added
        :raises ValueError: when values to add aren't the same length as table
        """
        if len(values) != self.table_length:
            raise ValueError(
                "Given values has to be the same length as table rows count")
        if self.table:
            for row, value in zip(self.table, values):
                row[field_name] = value
        else:
            for value in values:
                self.table.append({field_name: value})

    def parse_extra_column(self, index_or_header_value: Union[int, str],
                     func: Callable = int,
                     skip: Callable = lambda _: False,
                     separator: str = "") -> List[Any]:
        """
        Parses values from given column.

        :param index_or_header_value: either index of column to parse (negative
        indexing works too) or column name from table header (table has to have
        a header in that case)
        :param func: function to call on parsed text value, defaults to int
        :param skip: fucntion to call on every element that is going to be
        parsed when returns True element isn't parsed, defaults to lambda _:
        False
        :param separator: separator for text attributes given to `func`
        :return: list with parsed values
        """
        if isinstance(index_or_header_value, str):
            index = self._get_column_index_from_header(index_or_header_value)
        else:
            index = index_or_header_value
        if index < 0:
            index = self.row_length + index
        elements = self.html_table.css(
        f"{self.table_row_tag} > {self.row_column_tag}:nth-child({index+1})"
        )

        values = []
        for element in elements:
            if skip(element):
                continue
            values.append(func(element.text(separator=separator)))
        return values

    def rider_url(self) -> List[str]:
        return self._filter_a_elements("rider", True)

    def rider_name(self) -> List[str]:
        return self._filter_a_elements("rider", False)

    def team_url(self) -> List[str]:
        return self._filter_a_elements("team", True)

    def team_name(self) -> List[str]:
        return self._filter_a_elements("team", False)

    def stage_url(self) -> List[str]:
        return self._filter_a_elements("race", True)

    def stage_name(self) -> List[str]:
        return self._filter_a_elements("race", False)

    def nation_url(self) -> List[str]:
        nations_urls = self._filter_a_elements("nation", True)
        # return only urls to nation overview, not `pcs-season-wins`
        return [url for url in nations_urls if "pcs" not in url]

    def nation_name(self) -> List[str]:
        nations_texts = self._filter_a_elements("nation", False)
        # return text only when is not numeric, so doesn't represent number of
        # wins of the nation
        return [text for text in nations_texts
                if not text.isnumeric() and text != "-"]

    def age(self) -> List[int]:
        ages_elements = self.html_table.css(".age")
        return [int(age_e.text()) for age_e in ages_elements]

    def nationality(self) -> List[str]:
        flags_elements = self.html_table.css(".flag")
        flags = []
        for flag_e in flags_elements:
            if (flag_e.attributes['class'] and
                    " " in flag_e.attributes['class']):
                flags.append(flag_e.attributes['class'].split(" ")[1].upper())
        return flags

    def time(self) -> List[Optional[str]]:
        times_elements = self.html_table.css(".time")
        times = []
        for time_e in times_elements:
            time_e_text = time_e.text(separator="\n")
            rider_time = None
            for time_line in time_e_text.split("\n"):
                if ",," not in time_line and "″" not in time_line:
                    rider_time = time_line
                    break
            if rider_time == "-" or rider_time is None:
                rider_time = None
            else:
                rider_time = format_time(rider_time.replace(" ", ""))
            times.append(rider_time)
        return times

    def bonus(self) -> List[int]:
        """
        Parses all bonuses elements from the table. If there aren't any returns
        where every row has bonus 0.

        :return: list of bonuses
        """
        bonuses_elements = self.html_table.css(".bonis")
        bonuses = []
        for bonus_e in bonuses_elements:
            bonus = bonus_e.text().replace("″", "")
            if not bonus:
                bonus = 0
            else:
                bonus = int(bonus)
            bonuses.append(bonus)
        if not bonuses:
            bonuses = [0 for _ in range(self.table_length)]
        return bonuses

    def profile_icon(self) -> List[Literal[
        "p0", "p1", "p2", "p3", "p4", "p5"
    ]]:
        icons_elements = self.html_table.css(".icon.profile")
        profiles = []
        for icon_e in icons_elements:
            classes = icon_e.attributes['class']
            if classes and len(classes.split(" ")) >= 3:
                profiles.append(classes.split(" ")[-1])
        return profiles

    def season(self) -> List[Optional[int]]:
        """
        Parses all season elements text values from table. If value is not
        numeric sesaon is set to None.

        :return: list of seasons
        """
        seasons_elements = self.html_table.css(".season")
        seasons = []
        for season_e in seasons_elements:
            season_e_text = season_e.text()
            if season_e_text.isnumeric():
                seasons.append(int(season_e_text))
            else:
                seasons.append(None)
        return seasons

    def rank(self) -> List[Optional[int]]:
        possible_columns = ["Rnk", "pos", "Result", "#"]
        for column_name in possible_columns:
            try:
                return self.parse_extra_column(column_name,
                    lambda x: int(x) if x.isnumeric() else None)
            except ValueError:
                pass
        raise ValueError("Rank column wasn't found.")

    def status(self) -> List[Literal[
        "DF", "DNF", "DNS", "OTL", "DSQ"
    ]]:
        return self.parse_extra_column("Rnk",
            lambda x: "DF" if x.isnumeric() else x)

    def prev_rank(self) -> List[Optional[int]]:
        try:
            return self.parse_extra_column("Prev",
                lambda x: int(x) if x else None)
        except ValueError:
            return [None for _ in range(self.table_length)]

    def uci_points(self) -> List[Optional[float]]:
        try:
            return self.parse_extra_column("UCI",
                lambda x: float(x) if x else 0)
        except ValueError:
            return [0 for _ in range(self.table_length)]

    def pcs_points(self) -> List[Optional[int]]:
        try:
            return self.parse_extra_column("Pnt", lambda x: int(x) if x else 0)
        except ValueError:
            try:
                return self.parse_extra_column("PCS points",
                    lambda x: int(x) if x else 0)
            except ValueError:
                return [0 for _ in range(self.table_length)]

    def points(self) -> List[int]:
        return self.parse_extra_column("Points", float)

    def class_(self) -> List[str]:
        """
        Parses classes from table with a header. Method is called class_ so
        it won't be interchanged with class keyword. In parsed table underscore
        is removed.

        :return: list of classes
        """
        return self.parse_extra_column("Class", str)

    def first_places(self) -> List[Optional[int]]:
        return self.parse_extra_column("Wins", lambda x:
            int(x) if x.isnumeric() else 0)

    def second_places(self) -> List[Optional[int]]:
        return self.parse_extra_column("2nd", lambda x:
            int(x) if x.isnumeric() else 0)

    def third_places(self) -> List[Optional[int]]:
        return self.parse_extra_column("3rd", lambda x:
            int(x) if x.isnumeric() else 0)

    def distance(self) -> List[float]:
        return self.parse_extra_column("KMs", lambda x:
            float(x) if x else None)

    def date(self) -> List[str]:
        return self.parse_extra_column("Date", str)

    def rename_field(self, field_name: str, new_field_name: str) -> None:
        """
        Renames field from table.

        :param field_name: original field name
        :param new_field_name: new name of original field
        """
        for row in self.table:
            value = row.pop(field_name)
            row[new_field_name] = value

    def _get_column_index_from_header(self, column_name: str) -> int:
        if self.header is None:
            raise ExpectedParsingError(
                f"Can not parse '{column_name}' column without table header")
        for i, column_name_e in enumerate(self.header.css("th")):
            if column_name.lower() in column_name_e.text().lower():
                return i
        raise ValueError(
            f"'{column_name}' column isn't in table header")

    def _make_times_absolute(self, time_field: str = "time") -> None:
        """
        Sums all times from table with first time from table. Table has to have
        at least 2 rows.

        :param time_field: field which represents wanted time, defaults to
        `time`
        """
        first_time = self.table[0][time_field]
        for row in self.table[1:]:
            if row[time_field]:
                row[time_field] = add_times(first_time, row['time'])

    def _filter_a_elements(self, keyword: str, get_href: bool) -> List[str]:
        """
        Filters from all a elements these which has at the beggining of their
        href given keyword and gets their href or text.

        :param keyword: keyword that element's href should have
        :param get_href: whether to return the href of a element, when False
        text is returned
        :return: list of all a elements texts or hrefs with given keyword
        """
        filtered_values = []
        for a_element in self.a_elements:
            href = a_element.attributes['href']
            if href and href.split("/")[0] == keyword:
                if get_href:
                    filtered_values.append(href)
                else:
                    filtered_values.append(a_element.text())
        return filtered_values
