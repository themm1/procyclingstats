import re
from typing import Any, Dict, List

import re

from .errors import ExpectedParsingError, UnexpectedParsingError
from .scraper import Scraper
from .table_parser import TableParser
from .utils import get_day_month, parse_select, parse_table_fields_args


class Race(Scraper):
    """
    Scraper for race overview HTML page.

    Usage:

    >>> from procyclingstats import Race
    >>> race = Race("race/tour-de-france/2022")
    >>> race.enddate()
    '2022-07-24'
    >>> race.parse()
    {
        'category': 'Men Elite',
        'edition': 109,
        'enddate': '2022-07-24',
        'is_one_day_race': False,
        ...
    }

    """
    def year(self) -> int:
        """
        Parse year when the race occured from HTML.

        :return: Year when the race occured.
        """
        span = self.html.css_first("span.hideIfMobile")

        if not span:
            raise ExpectedParsingError("Span containing year not found")

        text = span.text().strip()

        match = re.search(r"(\d{4})", text)

        if not match:
            raise ExpectedParsingError(f"Impossible to parse year in '{text}'")

        return int(match.group(1))

    def name(self) -> str:
        """
        Parses display name from HTML.

        :return: Name of the race, e.g. ``Tour de France``.
        """
        h1 = self.html.css_first(".page-title > .title > h1")
        if not h1:
            raise ExpectedParsingError("Title not found")

        span = h1.css_first("span.hideIfMobile")
        full_text = h1.text()
        if span:
            full_text = full_text.replace(span.text(), "")

        return full_text.strip()

    def is_one_day_race(self) -> bool:
        """
        Parses whether race is one day race from HTML.

        :return: Whether given race is one day race.
        """
        titles = self.html.css("div > div > h4")
        titles = [] if not titles else titles
        for title_html in titles:
            if "Stages" in title_html.text():
                return False
        return True

    def nationality(self) -> str:
        """
        Parses race nationality from HTML.

        :return: 2 chars long country code in uppercase.
        """
        nationality_html = self.html.css_first(
            ".page-title > .title > span.flag")
        flag_class = nationality_html.attributes['class']
        return flag_class.split(" ")[1].upper() # type: ignore

    def edition(self) -> int:
        """
        Parses race edition year from HTML.

        :return: Edition as int.
        """
        h1 = self.html.css_first(".page-title > .title > h1")

        if not h1:
            raise ExpectedParsingError("Title not found")

        span = h1.css_first("span.hideIfMobile")
        full_text = h1.text()

        if span:
            edition_text = span.text().strip().split('\xa0')[2]
            edition_text = edition_text[:-2]  # remove 'th'/'st'/'nd'/'rd'
            return int(edition_text)
        raise ExpectedParsingError("Race cancelled, edition unavailable.")

    def startdate(self) -> str:
        """
        Parses race startdate from HTML.

        :return: Startdate in ``YYYY-MM-DD`` format.
        """
        startdate_html = self.html.css_first(
            ".list > li > div:nth-child(2)")
        return startdate_html.text()

    def enddate(self) -> str:
        """
        Parses race enddate from HTML.

        :return: Enddate in ``YYYY-MM-DD`` format.
        """
        enddate_html = self.html.css(".list > li > div:nth-child(2)")[1] 
        return enddate_html.text()

    def category(self) -> str:
        """
        Parses race category from HTML.

        :return: Race category e.g. ``Men Elite``.
        """
        category_html = self.html.css(".list > li > div:nth-child(2)")[2]
        return category_html.text()

    def uci_tour(self) -> str:
        """
        Parses UCI Tour of the race from HTML.

        :return: UCI Tour of the race e.g. ``UCI Worldtour``.
        """
        uci_tour_html = self.html.css(".list > li > div:nth-child(2)")[3]
        return uci_tour_html.text()

    def prev_editions_select(self) -> List[Dict[str, str]]:
        """
        Parses previous race editions from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        select_elements = self.html.css("div.selectNav select")

        for select in select_elements:
            options = select.css("option")
            values = [opt.attributes.get("value", "") for opt in options]

            # Match values that look like race/<race-name>/<year>/statistics/start
            if all(re.match(r"race/[^/]+/\d{4}/statistics/start", v) for v in values if v):
                return parse_select(select)
        return []

    def stages(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses race stages from HTML (available only on stage races). When
        race is one day race, empty list is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - date: Date when the stage occured in ``MM-DD`` format.
            - profile_icon: Profile icon of the stage (p1, p2, ... p5).
            - stage_name: Name of the stage, e.g \
                ``Stage 2 | Roskilde - Nyborg``.
            - stage_url: URL of the stage, e.g. \
                ``race/tour-de-france/2022/stage-2``.

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "date",
            "profile_icon",
            "stage_name",
            "stage_url",
        )
        if self.is_one_day_race():
            return []

        fields = parse_table_fields_args(args, available_fields)
        stages_table_html = self._find_header_table("Stages")
        if not stages_table_html:
            return []
        # remove rest day table rows
        for stage_e in stages_table_html.css("tbody > tr"):
            not_p_icon = stage_e.css_first(".icon.profile.p")
            if not_p_icon:
                stage_e.remove()

        # removes last row from stages table
        for row in stages_table_html.css("tr.sum"):
            row.remove()
        table_parser = TableParser(stages_table_html)
        casual_f_to_parse = [f for f in fields if f != "date"]
        table_parser.parse(casual_f_to_parse)

        # add stages dates to table if needed
        if "date" in fields:
            dates = table_parser.parse_extra_column(0, get_day_month)
            table_parser.extend_table("date", dates)
        return table_parser.table
    
    def stages_winners(self, *args) -> List[Dict[str, str]]:
        """
        Parses stages winners from HTML (available only on stage races). When
        race is one day race, empty list is returned.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - stage_name: Stage name, e.g. ``Stage 2 (TTT)``.
            - rider_name: Winner's name.
            - rider_url: Wineer's URL.
            - nationality: Winner's nationality as 2 chars long country code.

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "stage_name",
            "rider_name",
            "rider_url",
            "nationality",
        )
        if self.is_one_day_race():
            return []

        fields = parse_table_fields_args(args, available_fields)
        orig_fields = fields
        winners_html = self._find_header_table("Stage Winners")
        if not winners_html:
            return []
        # remove rest day table rows
        for stage_e in winners_html.css("tbody > tr"):
            stage_name = stage_e.css_first("td").text()
            if not stage_name:
                stage_e.remove()
        table_parser = TableParser(winners_html)
    
        casual_f_to_parse = [f for f in fields if f != "stage_name"]
        try:
            table_parser.parse(casual_f_to_parse)
        # if nationalities don't fit stages winners
        except UnexpectedParsingError:
            casual_f_to_parse.remove("nationality")
            if "rider_url" not in args:
                casual_f_to_parse.append("rider_url")
            table_parser.parse(casual_f_to_parse)
            nats = table_parser.nationality()
            j = 0
            for i in range(len(table_parser.table)):
                if j < len(nats) and \
                    table_parser.table[i]['rider_url'].split("/")[1]:
                    table_parser.table[i]['nationality'] = nats[j]
                    j += 1
                else:
                    table_parser.table[i]['nationality'] = None
                
                if "rider_url" not in orig_fields:
                    table_parser.table[i].pop("rider_url")
                    
        if "stage_name" in fields:
            stage_names = [val for val in
                table_parser.parse_extra_column(0, str) if val]
            table_parser.extend_table("stage_name", stage_names)
                    
        return table_parser.table
    
    def combative_riders(self) -> List[Dict[str, str]]:
        """
        Parses combative riders from HTML.

        :return: List of combative riders with keys ``stage``, ``rider_name``, ``rider_url``, ``rider_team_url``, and ``flag``.
        """
        # Construct the URL for combative riders
        combative_riders_url = self.url + "/results/combative-riders"
        combative_riders_html = self.fetch_html(combative_riders_url)
        
        if not combative_riders_html:
            raise ExpectedParsingError("Combative riders HTML fixture not found")
        
        # Locate the table of combative riders
        riders_table_html = combative_riders_html.css_first("table.basic")
        if not riders_table_html:
            print("No table found for combative riders.")  # Debugging log
            return []
        
        # Parse the table
        combative_riders = []
        for row in riders_table_html.css("tbody > tr"):
            # Extract stage data
            stage_cell = row.css_first("td:nth-child(1)")
            stage = stage_cell.text().strip() if stage_cell else "Unknown"
            
            # Extract rider data
            rider_cell = row.css_first("td:nth-child(2)")
            rider_name = None
            rider_url = None
            flag = None
            rider_team_url = None
            
            if rider_cell:
                # Extract flag (country code)
                flag_span = rider_cell.css_first("span.flag")
                if flag_span:
                    flag_classes = flag_span.attributes.get("class", "").split()
                    flag = flag_classes[1] if len(flag_classes) > 1 else None
                
                # Extract rider name and URL
                rider_link = rider_cell.css_first("a")
                if rider_link:
                    rider_name = rider_link.text().strip()
                    rider_url = rider_link.attributes.get("href", "").strip()
                
                # Extract team URL (if present in a separate link)
                team_link = rider_cell.css("a")
                if len(team_link) > 1:  # Assuming the second link is the team URL
                    rider_team_url = team_link[1].attributes.get("href", "").strip()
            
            # Append parsed data
            combative_riders.append({
                "stage": stage or None,
                "rider_name": rider_name or "Unknown",
                "rider_url": rider_url or None,
                "rider_team_url": rider_team_url or None,
                "flag": flag or "Unknown",
            })
        
        return combative_riders