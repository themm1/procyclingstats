from typing import Dict, List, Optional

from .scraper import Scraper


class TodayRaces(Scraper):
    """
    Scraper for the ProCyclingStats homepage to get today's races and results.

    Usage:

    >>> from procyclingstats import TodayRaces
    >>> today = TodayRaces()
    >>> today.live_races()
    [{'url': 'race/vuelta-a-la-comunidad-valenciana/2026/stage-2/live', 'name': 'Volta Comunitat Valenciana | Stage 2 (ITT)', ...}, ...]
    >>> today.finished_races()
    [{'url': 'race/uae-tour-women/2026/stage-1', 'name': 'UAE Tour Women', ...}, ...]
    >>> today.parse()
    {
        'live_races': [...],
        'finished_races': [...],
        'next_to_finish': [...],
        ...
    }
    """

    def __init__(self, html: Optional[str] = None, update_html: bool = True) -> None:
        """
        Creates TodayRaces scraper for the ProCyclingStats homepage.

        :param html: HTML to be parsed from, defaults to None.
        :param update_html: Whether to make request to homepage. Defaults to True.
        """
        # Pass the homepage URL (empty path resolves to BASE_URL)
        super().__init__("index.php", html=html, update_html=update_html)

    def live_races(self) -> List[Dict[str, str]]:
        """
        Parse currently live races from homepage.

        :return: List of dicts with live race info (url, name, status).
        """
        races = []
        live_list = self.html.css("ul.hp3-livestats li.live")
        
        for li in live_list:
            a_tag = li.css_first("a")
            if not a_tag:
                continue
                
            href = a_tag.attributes.get("href", "")
            title_span = li.css_first("span.title")
            name = title_span.text(strip=True) if title_span else ""
            
            # Get remaining km or riders
            togo_div = li.css_first("div.togo")
            togo = ""
            if togo_div:
                togo = togo_div.text(strip=True)
            
            races.append({
                "url": href,
                "name": name,
                "status": "live",
                "togo": togo
            })
        
        return races

    def next_to_finish(self) -> List[Dict[str, str]]:
        """
        Parse races that are next to finish.

        :return: List of dicts with race info (url, name, eta, category, class).
        """
        races = []
        table = self.html.css_first("table.next-to-finish tbody")
        
        if not table:
            return races
        
        for row in table.css("tr"):
            cells = row.css("td")
            if len(cells) < 4:
                continue
            
            # ETA
            eta = cells[1].text(strip=True) if len(cells) > 1 else ""
            
            # Race link and name
            a_tag = cells[3].css_first("a") if len(cells) > 3 else None
            if not a_tag:
                continue
                
            href = a_tag.attributes.get("href", "")
            name = a_tag.text(strip=True)
            
            # Category and class
            category = cells[4].text(strip=True) if len(cells) > 4 else ""
            race_class = cells[5].text(strip=True) if len(cells) > 5 else ""
            
            races.append({
                "url": href,
                "name": name,
                "eta": eta,
                "category": category,
                "class": race_class
            })
        
        return races

    def finished_races(self) -> List[Dict[str, str]]:
        """
        Parse races that finished today. Only return URL, name, and category.

        :return: List of dicts with race info.
        """
        races = []
        results_section = None
        for h3 in self.html.css("h3.black-info-title"):
            if "Results today" in h3.text():
                sibling = h3.next
                while sibling:
                    if sibling.tag == "ul" and "hp2-results" in sibling.attributes.get("class", ""):
                        results_section = sibling
                        break
                    sibling = sibling.next
                break
        if not results_section:
            return races
        for li in results_section.css("li.race"):
            race_link = li.css_first("div > a[href^='race/']")
            if not race_link:
                continue
            href = race_link.attributes.get("href", "")
            name_b = race_link.css_first("b")
            name = name_b.text(strip=True) if name_b else ""
            # Category info
            category_span = li.css_first("span.category")
            category = category_span.text(strip=True) if category_span else ""
            races.append({
                "url": href,
                "name": name,
                "category": category
            })
        return races

    def yesterday_races(self) -> List[Dict[str, str]]:
        """
        Parse races that finished yesterday. Only return URL, name, and category.

        :return: List of dicts with race info.
        """
        races = []
        results_section = None
        for h3 in self.html.css("h3.black-info-title"):
            if "Results yesterday" in h3.text():
                sibling = h3.next
                while sibling:
                    if sibling.tag == "ul" and "hp2-results" in sibling.attributes.get("class", ""):
                        results_section = sibling
                        break
                    sibling = sibling.next
                break
        if not results_section:
            return races
        for li in results_section.css("li.race"):
            race_link = li.css_first("div > a[href^='race/']")
            if not race_link:
                continue
            href = race_link.attributes.get("href", "")
            name_b = race_link.css_first("b")
            name = name_b.text(strip=True) if name_b else ""
            # Category info
            category_span = li.css_first("span.category")
            category = category_span.text(strip=True) if category_span else ""
            races.append({
                "url": href,
                "name": name,
                "category": category
            })
        return races
