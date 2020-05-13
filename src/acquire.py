import logging
import json
import numpy as np
import pandas as pd
import logging

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
logging_level = "INFO"

logger = logging.getLogger('acquire.py')
logger.setLevel(logging_level)

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
        ids (`numpy.array`):
        batch_size (`int`):

    Returns:

    """
    # Instantiate API client
    bgg = BGGClient(requests_per_minute=requests_per_minute)

    # Form batches
    number_of_ids = len(ids)
    remainder = number_of_ids % batch_size
    ids_no_remainder = ids[:number_of_ids-remainder] # Making sure ids are divisible by batch_size
    batches = ids_no_remainder.reshape(int(len(ids_no_remainder)/batch_size),batch_size)
    batches = list(batches) # Converting from np.ndarray to regular list
    batches = [lst.tolist() for lst in batches] # converting each batch to regular list

    # Fetch batches via API
    batch_number = 0
    batches_successful = 0
    batches_failed = 0
    games = []
    for batch in batches:
        logger.debug(f"Fetching data for batch number {batch_number} / {len(batches)}")
        try:
            game_batch = bgg.game_list(batch)
            batches_successful += 1
            logging.debug(f"Successfully fetched games in batch number {batch_number}")
            games.extend(game_batch)
        except BGGAPiError:
            batches_failed += 1
            logging.debug(f"Failed to fetch games data for batch number {batch_number}")

        batch_number += 1

    logging.info(f"Successful Batches: {batches_successful} ")
    logging.info(f"Failed Batches: {batches_failed} ")

    # Fetch remaining games, which didn't fit in a batch
    remainder_ids = list(ids[len(ids_no_remainder):])
    remainder_ids_successful = 0
    remainder_ids_failed = 0
    for id in remainder_ids:
        try:
            game = bgg.game(game_id=id)
            logger.debug(f"Successfully fetched remainder game with id {id}")
            remainder_ids_successful += 1
            games.append(game)
        except BGGApiError:
            logger.debug(f"Failed to fetch remainer game with id {id}")
            remainder_ids_successful += 1

    if remainder_ids_successful != 0:
        logging.info(f"Successfully fetched {remainder_ids_successful} remainder games")
    if remainder_ids_failed != 0:
        logging.info(f"Failed to fetch {remainder_ids_failed} remainder games")

    logging.info(f"Total games successfully fetched: {batch_size*batches_successful+remainder_ids_successful}")
    logging.info(f"Total games failed to fetch: {batch_size * batches_failed+ remainder_ids_failed}")

    return games



def convert_game_to_dict(game):
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
    ids = fetch_game_ids(url)
    games = batch_api_call(ids)

    dict_games = []
    for game in games:
        try:
            dict_game = convert_game_to_dict(game)
            dict_games.append(dict_game)
        except:
            logging.debug(f"Failed to convert to dict game with id {game.id}")

    with open('games.json', 'w') as fp:
        json.dump(dict_games, fp)



