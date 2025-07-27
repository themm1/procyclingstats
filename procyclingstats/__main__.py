import argparse
import sys
from pprint import pprint  # pylint: disable=unused-import
from typing import Any, Dict, List, Tuple, Type

from tabulate import tabulate

# imports all scraping classes that are listed in `scraper_classes` tuple and
# Scraper class
from .__init__ import (Race, RaceClimbs, RaceStartlist, Ranking, Rider,
                       RiderResults, Scraper, Stage, Team, RaceCombativeRiders)

scraper_classes = (
    Race,
    RaceStartlist,
    Ranking,
    Rider,
    Stage,
    Team,
    RiderResults,
    RaceClimbs,
    RaceCombativeRiders
)

def configure_parser():
    parser = argparse.ArgumentParser(
        prog="python -m procyclingstats",
        description=
        ("CLI to procyclingstats package. Scraper object to parse " +
        "given URL is evaluated automatically. When no scraper object is " +
        "able to parse given URL ValueError is raised. When ran in " +
        "interactive mode, nothing is printed and scraper object ready " +
        "for parsing is available as `obj`.")
    )
    parser.add_argument("url", metavar="url", type=str,
                        help="Absolute or relative URL of PCS page to parse.")
    parser.add_argument("--fulltable", action="store_const", const=True,
            default=False,
            help="Whether to print full or shortened tables in output.")
    return parser

def get_corresponding_scraping_class(relative_url: str) -> Any:
    """
    Returns scraping class for given URL (!!!does not work 100% of times!!!).

    :param relative_url: Relative URL of some PCS page.
    :return: Scraping class for the URL. None when not found.
    """
    splitted_url = relative_url.split("/")
    if "comative-riders" in splitted_url or "combative-riders" in splitted_url:
        return RaceCombativeRiders
    if (splitted_url[0] == "rider" and "results" in splitted_url) or \
        (relative_url[:9] == "rider.php"):  
        return RiderResults
    elif splitted_url[0] == "rider":
        return Rider
    elif len(splitted_url) >= 4 and splitted_url[0] == "race" and \
        ("stage" in splitted_url[3] or "gc" in splitted_url[3] or "prologue" \
        in splitted_url[3] or "result" in splitted_url):
        return Stage
    elif "rankings" in relative_url:
        return Ranking
    elif splitted_url[0] == "race" and "startlist" in splitted_url:
        return RaceStartlist
    elif "team" == splitted_url[0]:
        return Team
    elif splitted_url[0] == "race" and "climbs" in splitted_url:
        return RaceClimbs
    elif splitted_url[0] == "race":
        return Race
    return None

def run(args: argparse.Namespace) -> Scraper:
    """
    Runs CLI script with given arguments.

    :param args: Argparse arguments (currently 'url' and 'fulltable').
    :return: Scraper object created from given URL.
    """
    scraper_class = get_corresponding_scraping_class(args.url)
    scraper_obj = scraper_class(args.url)

    # object created, so return when running in interactive mode
    if sys.flags.interactive:
        print(f"Scraper object `{scraper_obj}` can now be accessed as `obj`.")
        return scraper_obj

    tables = {}
    # print basic one line data
    for key, value in scraper_obj.parse().items():
        if isinstance(value, list) and value:
            tables[key] = value
        else:
            print(key + ": " + str(value))

    # print tables
    for key, value in tables.items():
        print()
        print(key + ":")
        # tabulate full table
        if args.fulltable or len(value) <= 13:
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
    return scraper_obj

def tab(table: List[Dict[str, Any]]) -> None:
    """
    Utility function for easier table tabulating when running in interactive
    mode.

    :param table: Table to tabulate.
    """
    print(tabulate(table, headers="keys"))

if __name__ == "__main__":
    arguments = configure_parser().parse_args()
    obj = run(arguments)
