# Example of using procyclingstats package asynchronously. Third party
# "requests_futures" package is needed to run the example.
import time
from concurrent.futures import as_completed
from pprint import pprint

from procyclingstats import Ranking, Rider
from requests_futures.sessions import FuturesSession


def main():
    ranking = Ranking("rankings/me/individual-season").individual_ranking()
    # get heights of first 50 riders from the ranking asynchronously
    futures_heights = ranking_heights_future(ranking)
    # get heights of first 50 riders from the ranking synchronously
    heights = ranking_heights(ranking)
    pprint(futures_heights)

def ranking_heights_future(ranking):
    t1 = time.time()
    session = FuturesSession()
    # initialize list with future sessions
    future_sessions = []
    # make requests to all stage pages asynchronously and store them in a list
    for row in ranking[:50]:
        # create absolute URL from stage_url in the table
        # start making request to the URL
        url = "https://www.procyclingstats.com/" + row['rider_url']
        future_session = session.get(url)
        future_sessions.append(future_session)

    # create rider objects from obtained HTMLs and store heights in 
    # riders_heights dict, make sure you don't use
    # concurrent.futures.as_completed(future_sessions)
    # in the for loop, because in that case the order of riders won't be
    # preserved
    riders_heights = {}
    for i, future_session in enumerate(future_sessions):
        html = future_session.result().text
        rider = Rider(ranking[i]['rider_url'], html=html, update_html=False)
        riders_heights[rider.normalized_relative_url()] = rider.height()
    print("With requests_futures package:", time.time() - t1)
    return riders_heights
    
def ranking_heights(ranking):
    t1 = time.time()
    riders_heights = {}
    for row in ranking[:50]:
        rider = Rider(row['rider_url'])
        riders_heights[rider.normalized_relative_url()] = rider.height()
    print("Without requests_futures package:", time.time() - t1)
    return riders_heights

if __name__ == "__main__":
    main()
