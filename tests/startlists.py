from procyclingstats.stage_scraper import Stage
from procyclingstats.race_scraper import Race

# non empty list
assert([] != Stage("race/giro-d-italia/2021/stage-1").startlist())
assert([] != Stage("race/giro-d-italia/2025/stage-9").startlist())
assert([] != Stage("race/tour-de-france/2024/").startlist())
assert([] != Race("race/paris-roubaix/2025").startlist())

# standard output
print(Stage("race/giro-d-italia/2021/stage-1").startlist())
print(Stage("race/giro-d-italia/2025/stage-9").startlist())
print(Stage("race/tour-de-france/2024/").startlist())
print(Race("race/paris-roubaix/2025").startlist())