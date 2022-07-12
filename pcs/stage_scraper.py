from typing import Literal, Union, List, Dict, Any
from pprint import pprint
import requests_html
from tabulate import tabulate
from requests_html import HTML
from utils import RequestWrapper, convert_date, add_time 
from race_scraper import Race


def test():
    s = Stage("race/tour-de-france/2022/stage-v")
    s.update_html()
    s.parse_html()
    # pprint(s.content['info'])
    print(tabulate(s.results()))
    # print(tabulate(s.gc()))
    # print(tabulate(s.points()))
    # print(tabulate(s.kom()))
    # print(tabulate(s.youth()))
    # print(tabulate(s.teams()))


class Stage(RequestWrapper):
    """
    Parses information about stage from given `stage_url`
    
    Attributes:
        url: stage's URL
        print_request_url: whether to print URL of request when making request
        html: HTML from URL, `None` on default
        content: dict with parsed information, call `self.parse_html` to update
    Args:
        stage_url: stage's URL, e.g. `race/tour-de-france/2015/stage-18`
        print_request_url: whether to print URL of request when making request
    see base class for other inhereted attributes
    """
    _course_translator = {
            "p0": (None, None),
            "p1": ("flat", 0),
            "p2": ("hilly", 0),
            "p3": ("hilly", 1),
            "p4": ("mountain", 0),
            "p5": ("mountain", 1),
    }
    _tables_path = ".result-cont > table > tbody"
    def __init__(self, stage_url: str, print_request_url: bool=True) -> None:
        Race._validate_url(stage_url, stage_url, stage=True)
        super().__init__(stage_url, print_request_url)
        
    def parse_html(self) -> Dict[str, Any]:
        """
        Store all parsable info to `self.content` dict
        :returns: `self.content` dict
        """
        self.content['info'] = {
                "stage_id": self.stage_id(),
                "race_season_id": self.race_season_id(),
                "distance": self.distance(),
                "mtf": self.mtf(),
                "course_type": self.course_type(),
                "race_type": self.stage_type(),
                "winning_attack_length": self.winning_attack_length(),
                "vertical_meters": self.vertical_meters(),
                "date": self.date(),
                "departure": self.departure(),
                "arrival": self.arrival()
        }
        self.content['results'] = self.results()
        # When the race is stage race, add classifications
        if self.is_stage_race():
            self.content['gc'] = self.gc()
            self.content['points'] = self.points()
            self.content['kom'] = self.kom()
            self.content['youth'] = self.youth()
            self.content['teams'] = self.teams()
        return self.content

    
    def race_season_id(self) -> str:
        """
        :returns: race season id parsed from URL e.g. `tour-de-france/2021`
        """
        return "/".join(self.url.split("/")[1:3])
    
    def stage_id(self) -> str:
        """
        :returns: stage id parsed from URL e.g. `tour-de-france/2021/stage-9`
        """
        url_elements = self.url.split("/")[1:]
        stage_id = [element for element in url_elements if element != "result"]
        return "/".join(stage_id)

    def is_stage_race(self) -> bool:
        """:returns: whether the race is a stage race"""
        # If there are elements with .restabs class (Stage/GC... menu), the race
        # is a stage race
        return len(self.html.find(".restabs")) > 0

    def distance(self) -> float:
        """:returns: distance of the stage"""
        distance_html = self.html.find(".infolist > li:nth-child(5) > div")
        return float(distance_html[1].text.split(" km")[0])
    
    def mtf(self) -> bool:
        """:returns: bool whether the stage has mountain finnish"""
        profile_html = self.html.find(".infolist > li:nth-child(7) > \
            div:nth-child(2) > span")       
        profile = profile_html[0].attrs['class'][2] 
        return bool(self._course_translator[profile][1])
    
    def course_type(self) -> Union[Literal["flat", "hilly", "mountain"], None]:
        """:returns: course type"""
        profile_html = self.html.find(".infolist > li:nth-child(7) > \
            div:nth-child(2) > span")       
        profile = profile_html[0].attrs['class'][2] 
        return self._course_translator[profile][0]
    
    def stage_type(self) -> Literal["itt", "ttt", "rr"]:
        """:returns: type of stage"""
        stage_name_html = self.html.find(".sub > .blue")
        stage_name = stage_name_html[0].text
        if "(ITT)" in stage_name:
            return "itt"
        elif "(TTT)" in stage_name:
            return "ttt"
        else:
            return "rr"
        
    def winning_attack_length(self, when_none_or_unknown: float=0.0) -> float:
        """
        :param when_none_or_unknown: value to return when there is no info \
            about winning attack
        :returns: length of winning attack"""
        won_how_html = self.html.find(".infolist > li:nth-child(12) > div")
        won_how = won_how_html[1].text
        if " km solo" in won_how:
            return float(won_how.split(" km sol")[0])
        else:
            return when_none_or_unknown
        
    def vertical_meters(self) -> int:
        """:returns: vertical meters gained throughout the stage"""
        vertical_meters_html = self.html.find(".infolist > li:nth-child(9) \
            > div")
        vertical_meters = vertical_meters_html[1].text
        return int(vertical_meters) if vertical_meters else None
    
    def date(self) -> str:
        """:returns: date when stage took place `yyyy-mm-dd"""
        date_html = self.html.find(f".infolist > li > div")
        date = date_html[1].text.split(", ")[0]
        return convert_date(date)
    
    def departure(self) -> str:
        """:returns: departure of the stage"""
        departure_html = self.html.find(".infolist > li:nth-child(10) > div")
        return departure_html[1].text
        
    def arrival(self) -> str:
        """:returns: arrival of the stage"""
        arrival_html = self.html.find(".infolist > li:nth-child(11) > div")
        return arrival_html[1].text

    def results(self) -> List[dict]:
        """
        Parses main results table to list of dict
        :returns: table with columns `rider_id`, `team_id`, `rank`, \
            `status`, `bonus_seconds` represented as list of dicts
        """
        # remove other result tables from html
        # because of one day races self._table_index isn't used here
        categories = self.html.find(self._tables_path)
        results_html = HTML(html=categories[0].html)

        if self.stage_type() == "ttt":
            return self._parse_ttt_results_table(results_html)
        else:
            return self._parse_time_table_with_bonuses(results_html, 
                gc=False)
    
    def gc(self) -> List[dict]:
        """
        Parses GC results table to list of dict
        :returns: table with columns `rider_id`, `team_id`, `rank`, \
            `bonus_seconds` represented as list of dicts, empty when not found 
        """
        # remove other result tables from html
        categories = self.html.find(self._tables_path)
        gc_table_index = self._table_index("gc")
        if gc_table_index == None:
            return []
        gc_html = HTML(html=categories[gc_table_index].html)
        results = self._parse_time_table_with_bonuses(gc_html, gc=True)
        return results
    
    def points(self) -> List[dict]:
        """
        Parses points classification table to list of dict
        :returns: table with columns `rider_id`, `team_id`, `rank`, `points`, \
            `delta_points` represented as list of dicts, empty when not found
        """
        points_table_index = self._table_index("points") 
        # return if stage doesn't have points classification
        if points_table_index == None:
            return []
        # remove other result tables from html
        categories = self.html.find(self._tables_path)
        points_html = HTML(html=categories[points_table_index].html)
        points_table = self._parse_points_table(points_html)
        return points_table

    def kom(self) -> List[dict]:
        """
        Parses kom classification table to list of dict
        :returns: table with columns `rider_id`, `team_id`, `rank`, `points`, \
            `delta_points` represented as list of dicts, empty when not found
        """
        kom_table_index = self._table_index("kom") 
        # return if stage doesn't have KOM classification
        if kom_table_index == None:
            return []

        # remove other result tables from html
        categories = self.html.find(self._tables_path)
        kom_html = HTML(html=categories[kom_table_index].html)
        kom_table = self._parse_points_table(kom_html)
        return kom_table
    
    def youth(self) -> List[dict]:
        """
        Parses youth classification table to list of dict
        :returns: table with columns `rider_id`, `team_id`, `rank`,`time` \
            represented as list of dicts, empty list when not found
        """
        youth_table_index = self._table_index("youth")
        # return if stage doesn't have youth classification
        if youth_table_index == None:
            return []
        # remove other result tables from html
        categories = self.html.find(self._tables_path)
        youth_html = HTML(html=categories[youth_table_index].html)
        youth_table = self._parse_time_table(youth_html)
        return youth_table

    def teams(self) -> List[dict]:
        """
        Parses team time classification table to list of dict
        :returns: table with columns `team_id`, `rank`, `time` represented as \
            list of dicts, empty list when not found
        """
        teams_table_index = self._table_index("teams")
        # return if stage doesn't have youth classification
        if teams_table_index == None:
            return []
        # remove other result tables from html
        categories = self.html.find(".result-cont")
        teams_html = HTML(html=categories[teams_table_index].html)
        teams_table = self._parse_time_table(teams_html, teams=True)
        return teams_table

    def _table_index(self, table: Literal["stage", "gc", "points", "kom",
            "youth", "teams"]) -> Union[int, None]:
        """
        Get index of HTML .result-cont table with results based on `table` param
        :param table: keyword of wanted table that occures in .restabs menu
        :returns: index of wanted HTML table, None when not found
        """
        table_index = None
        for i, element in enumerate(self.html.find("ul.restabs > li > a")):
            if table in element.text.lower():
                table_index = i
        return table_index
    
    def _points_index(self, html: requests_html.HTML) -> Union[int, None]:
        """
        Get index of column with points from HTML table
        :param html: HTML table to be parsed from
        :returns: index of columns with points, None when not found
        """
        points_index = None
        elements = html.find("tbody > tr:first-child > td")
        for i, element in enumerate(reversed(elements)):
            if element.text.isnumeric():
                points_index = len(elements) - i
                break
        return points_index

    def _parse_time_table_with_bonuses(self, html: requests_html.HTML,
            gc: bool=False) -> List[dict]:
        """
        Parse results HTML table with times and bonuses (stage/gc)
        :param html: HTML table to be parsed from
        :param gc: whether the HTML table is table with GC results (whether to \
            include status value to parsed table)
        :returns: parsed table represented as list of dicts
        """
        first_time_html = html.find("td.time.ar")[0]
        ranks_html = html.find("td:first-child")
        times_html = html.find("td.time.ar > div.hide")
        ids_html = html.find("td:nth-child(6) > div > a")
        teams_html = html.find("td.cu600 > a")
        bonuses_html = html.find("td.bonis")
        
        # add None times for riders who haven't finnished
        for _ in range(len(ranks_html)-len(times_html)):
            times_html.append(None)
        # add None bonuses when there aren't any
        for _ in range(len(ranks_html)-len(bonuses_html)):
            bonuses_html.append(None)
        first_time = first_time_html.text.split("\n")[0]
        zipped_htmls = zip(ranks_html, ids_html, teams_html, times_html,
            bonuses_html)

        # loop over results table
        results = []
        for i, (rank_html, id_html, team_id_html, time_html, bonus_html) in \
            enumerate(zipped_htmls):
            # rider did finnish
            if not gc and rank_html.text.isnumeric():
                position = i + 1
                status = "DF"
            # either DNF, DNS or DSQ
            elif not gc:
                position = None
                status = rank_html.text
            # When add_status is False, so every rider in table aren't any DNFs,
            # DSQs...
            else:
                position = i + 1
            rider_id = id_html.attrs['href'].split("/")[1]
            team_id = team_id_html.attrs['href'].split("/")[1]
            if time_html != None:
                # rider did not finnish
                if time_html.text == "-":
                    time = None
                # add rider's time to first time if current rider isn't first,
                # because riders times are written on page relativly to winner
                else:
                    if i != 0:
                        time = add_time(first_time, time_html.text)
                    else:
                        # Convert first time to time which is in {days time} 
                        # format
                        time = add_time(first_time, "00:00:00")

            # set bonus to riders that gained some
            if bonus_html != None and bonus_html.text:
                bonus = int(bonus_html.text[:-1])
            else:
                bonus = 0
            results.append({
                "rider_id": rider_id,
                "team_id": team_id,
                "rank": position,
                "time": time,
                "bonus_seconds": bonus
            })
            if not gc:
                results[i]['status'] = status
        return results
    
    def _parse_time_table(self, html: requests_html.HTML, teams: bool=False) ->\
        List[dict]:
        """
        Parse results HTML table with times and without bonuses (teams/youth/\
            one day races)
        :param html: HTML table to be parsed from
        :param teams: whether the HTML table is table with team time results (\
            whether to include rider_id value to parsed table)
        :returns: parsed table represented as list of dicts
        """
        if teams:
            ids_html = html.find("td:nth-child(4) > a")
        else:
            ids_html = html.find("td:nth-child(6) > div > a")
            teams_html = html.find("td.cu600 > a")
        first_time_html = html.find("td.time.ar")[0]
        times_html = html.find("td.time.ar > .hide")

        first_time = first_time_html.text.split("\n")[0]
        zipped_htmls = zip(ids_html, times_html)
        
        # loop over results table
        results = []
        for i, (id_html, time_html) in enumerate(zipped_htmls):
            position = i + 1
            id_ = id_html.attrs['href'].split("/")[1]

            if i != 0:
                time = add_time(first_time, time_html.text)
            else:
                # Convert first time to time which is in {days time} format
                time = add_time(first_time, "00:00:00")

            results.append({
                "rank": position,
                "time": time,
            })
            if teams:
                results[i]['team_id'] = id_
            else:
                results[i]['rider_id'] = id_
                team_id = teams_html[i].attrs['href'].split("/")[1]
                results[i]['team_id'] = team_id

        return results

    def _parse_points_table(self, html: requests_html.HTML) -> List[dict]:
        """
        Parse results HTML table with points (points/kom classifications)
        :param html: HTML table to be parsed from
        :returns: parsed table represented as list of dicts
        """
        points_index = self._points_index(html)
        # return if points index wasn't found
        if points_index == None:
            return []
        ids_html = html.find("td:nth-child(6) > div > a")
        points_html = html.find(f"tr > td:nth-child({points_index})")
        delta_points_html = html.find(f"tr > td.delta_pnt")
        teams_html = html.find("td.cu600 > a")

        zipped_htmls = zip(ids_html, teams_html, points_html, delta_points_html)

        # loop over results table
        results = []
        for i, (rider_id_html, team_id_html, points_html, delta_points_html) in \
            enumerate(zipped_htmls):
            position = i + 1
            rider_id = rider_id_html.attrs['href'].split("/")[1]
            team_id = team_id_html.attrs['href'].split("/")[1]
            # rider doesn't have any points
            if points_html.text == "":
                continue
            points = int(points_html.text)
            # set delta_points to 0 when points didn't change, else update to 
            # delta
            if delta_points_html.text == "-":
                delta_points = 0
            else:
                delta_points = int(delta_points_html.text)

            results.append({
                "rider_id": rider_id,
                "team_id": team_id,
                "rank": position,
                "points": points,
                "delta_points": delta_points
            })
        return results
    
    def _parse_ttt_results_table(self, html: requests_html.HTML) -> List[dict]:
        """
        Parse results HTML table from team time trial
        :param html: HTML table to be parsed from
        :returns: parsed table represented as list of dicts
        """
        # Info about current table row
        current_position = 0
        current_team_id = ""
        current_team_time = "00:00:00"
        results = []
        for element in html.find("tr"):
            current_html = HTML(html=element.html)
            # Update current table row info because we are parsing new team
            if "team" in element.attrs['class']:
                current_team_id = current_html.find("td > a")[0].attrs['href']
                current_team_time = current_html.find("td:nth-child(3)")[0].text
                current_position += 1
                current_team_time = add_time(current_team_time, "00:00:00")
            # Add rider to parsed table
            else:
                rider_id = current_html.find("td > a")[0].attrs['href']
                results.append({
                    "rank": current_position,
                    "team_id": current_team_id.split("/")[1],
                    "rider_id": rider_id.split("/")[1],
                    "time": current_team_time,
                    "bonus_seconds": 0
                })
        return results


if __name__ == "__main__":
    test()