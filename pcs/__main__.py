import sys
# importing in case module is ran in interactive mode
from pprint import pprint
from typing import List

from tabulate import tabulate

from .race_edition_scraper import RaceEdition
from .ranking_scraper import Ranking
from .rider_scraper import Rider
from .scraper import Scraper
from .stage_scraper import Stage
from .startlist_scraper import Startlist
from .team_scraper import Team


def tab(table: List[dict]) -> None:
    """
    Utility function for easier table tabulating when running in interactive
    mode.

    :param table: table to tabulate
    """
    print(tabulate(table, headers="keys"))
    

def get_scraper_obj_by_url(scraper_classes: List[Scraper],
                           url: str) -> Scraper:
    """
    Gets scraper class that can parse HTML from given URL

    :param url: pcs URL
    :raises ValueError: When no class is able to parse the URL
    :return: object created from given URL
    """
    for ScraperClass in scraper_classes:
        try:
            ScraperClass(url, None, False)
            return ScraperClass
        except ValueError:
            pass
    raise ValueError(f"Invalid URL: {url}")


class CLI:
    """
    Command line interface for interacting with scraper classes. When module is
    ran all parsed data from given URL are printed in nice format. When module
    is ran in interactive mode, object named `obj` is created and user can call
    methods manually. Fucntions for printing as `pprint` or `tabulate` are
    imported too.
    example usage: `python -m pcs rider/tadej-pogacar`

    Positional arguments:
    - `url`: URL to be parsed from. When no parser object is able to parse data
    from HTML of given URL ValueError is raised.

    Optional args:
    - `-fulltable`: whether to print full table or only first and last rows,
    defaults to False
    - `-print_tables`: whether to print tables parsed from the HTML, defaults
    to True
    """

    scraper_classes = [
        RaceEdition,
        Startlist,
        Ranking,
        Rider,
        Stage,
        Team
    ]
    arg_error = ValueError("Please provide a URL")

    def __init__(self):
        self.args = sys.argv[1:]
        self.set_url()
        self.set_fulltable()
        self.set_print_tables()
        
    def set_url(self):
        for arg in self.args:
            if arg != "-": 
                self.url = arg
                return
        raise self.arg_error
        
    def set_fulltable(self):
        if "-fulltable" in self.args:
            self.fulltable = True
        else:
            self.fulltable = False
            
    def set_print_tables(self):
        if "-skip_tables" in self.args:
            self.print_tables = True
        else:
            self.print_tables = False
            
    def run(self):
        scraper_class = get_scraper_obj_by_url(self.scraper_classes, self.url)
        scraper_obj = scraper_class(self.url)
        
        # object created, so return when running in interactive mode
        if sys.flags.interactive:
            return scraper_obj

        tables = {}
        # print basic one line data
        for key, value in scraper_obj.parse().items():
            if isinstance(value, list) and value:
                tables[key] = value
            else:
                print(key + ": " + str(value))
        if self.print_tables:
            return

        # print tables
        for key, value in tables.items():
            print()
            print(key + ":")
            # tabulate full table
            if self.fulltable or len(value) <= 13:
                print(tabulate(value, headers="keys"))
            # tabulate shortened table (first and last 5 rows of table with dots
            # inbetween
            else:
                shortened_table = value[:5]
                for _ in range(3):
                    shortened_table.append({})
                    for key in shortened_table[0].keys():
                        shortened_table[-1][key] = "..."
                shortened_table.extend(value[-5:])
                print(tabulate(shortened_table, headers="keys"))


if __name__ == "__main__":
    c = CLI()
    obj = c.run()
