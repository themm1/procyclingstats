from pprint import pprint

from procyclingstats import Race, RaceClimbs, Stage

# RACE_URL can be replaced with any valid stage race URL
RACE_URL = "race/tour-de-france/2022"
race = Race(f"{RACE_URL}/overview")
race_climbs = RaceClimbs(f"{RACE_URL}/route/climbs")

stages = race.stages()
climbs_table = race_climbs.climbs()
# make dict to access climbs by their URLs
climbs = {climb['climb_url']: climb for climb in climbs_table}

stages_climbs = {}
# group climbs by stages
for stage_info in stages:
    stage = Stage(stage_info['stage_url'])
    stage_climbs = [climbs[s['climb_url']] for s in stage.climbs()]
    stages_climbs[stage_info['stage_url']] = stage_climbs
    
pprint(stages_climbs) 
