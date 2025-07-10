import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from procyclingstats import (Race, RaceClimbs, RaceStartlist, Ranking, Rider,
                       RiderResults, Scraper, Stage, Team)

""" Example usage of the ProCyclingStats scraper classes. Can be used to sanity check the functionality of the classes. """

RACE_URL = "race/tour-de-france/2022"
race = Race(f"{RACE_URL}/overview")

print('RACE CLASS')
for method in race.parse().keys():
    print(f"{method}: {race.parse()[method]}")

print('RACE CLIMBS CLASS')
race_climbs = RaceClimbs(f"{RACE_URL}/route/climbs")
for method in race_climbs.parse().keys():
    print(f"{method}: {race_climbs.parse()[method]}")

print('RACE STARTLIST CLASS')
race_start = RaceStartlist(f"{RACE_URL}/startlist")
for method in race_start.parse().keys():
    print(f"{method}: {race_start.parse()[method]}")

print('RANKING CLASS')
ranking = Ranking("rankings/me/individual")
print(ranking.individual_ranking()[0:5])  # Display first 5 entries

print('RIDER CLASS')
rider = Rider("rider/tadej-pogacar")
for method in rider.parse().keys():
    print(f"{method}: {rider.parse()[method]}")

print('RIDER RESULTS')
rider_results = RiderResults("rider/tadej-pogacar/results")
for method in rider_results.parse().keys():
    print(f"{method}: {rider_results.parse()[method]}") 

print('Stage CLASS')
stage = Stage("race/tour-de-france/2022/stage-18")
for method in stage.parse().keys():
    print(f"{method}: {stage.parse()[method]}")

print('Team CLASS')
team = Team("team/uae-team-emirates/2022")
for method in team.parse().keys():
    print(f"{method}: {team.parse()[method]}")

