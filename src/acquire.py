import logging
import json
import numpy as np
import pandas as pd
from boardgamegeek import BGGClient
from boardgamegeek.exceptions import BGGApiError, BGGError, BGGItemNotFoundError, BGGValueError

# todo: add logging
# todo: add docstrings
# todo: add exception handling
# todo: outsource configurations

# CONFIGURATIONS
url = "https://raw.githubusercontent.com/beefsack/bgg-ranking-historicals/master/2019-07-08.csv"
requests_per_minute = 100
batch_size = 100

# FUNCTIONS
def fetch_game_ids(url: str) -> list:
    """

    Args:
        url (`str`): the url

    Returns:

    """
    df = pd.read_csv(url)
    return df['ID'].values

def batch_api_call(ids,batch_size=100):
    """

    Args:
        ids:
        batch_size:

    Returns:

    """
    # Instantiate API client
    bgg = BGGClient(requests_per_minute=requests_per_minute)

    # Calculate number of batches
    number_of_ids = len(ids)
    remainder = number_of_ids % batch_size
    ids_no_remainder = ids[:number_of_ids-remainder] # Making sure ids are divisible by batch_size
    batches = ids_no_remainder.reshape(int(len(ids_no_remainder)/batch_size),batch_size)
    batches = list(batches) # Converting from np.ndarray to regular list
    batches = [lst.tolist() for lst in batches] # converting each batch to regular list

    batch = 0
    games = []
    for batch in batches:
        bgg.game_list()



    return games



def convert_game_to_json(game):
    """Extract all useful information from a game object and return as a dictionary

    Args:
        game:

    Returns:

    """
    dict_game = {}
    dict_game['id'] = game.id
    dict_game['name'] = game.name
    dict_game['stats'] = game.stats
    dict_game['image'] = game.image
    dict_game['thumbnail'] = game.thumbnail
    dict_game['artists'] = game.artists
    dict_game['designers'] = game.designers
    dict_game['year'] = game.year
    dict_game['description'] = game.description
    dict_game['categories'] = game.categories
    dict_game['mechanics'] = game.mechanics
    dict_game['min_age'] = game.min_age
    dict_game['publishers'] = game.publishers

    return dict_game


if __name__ == "__main__":
    # Instantiate API client
    bgg = BGGClient(requests_per_minute=requests_per_minute)


