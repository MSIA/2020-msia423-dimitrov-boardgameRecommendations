"""
This modules fetches up-to-date data on 17,313 games from BoardGameGeek.com (BGG) and writes it to a json file.

You should expect it to take ~5-10 minutes. Thank you for your patience.

It does this via a package called "boardgamegeek", which serves as a convenient wrapper for BGG's XML API2.

See "notebooks/develop/Exploring_BGG_API_Wrapper.ipynb" for example usage of the wrapper.

Documentation for the package: https://lcosmin.github.io/boardgamegeek/#quick-install
Documentation for the XML API: https://boardgamegeek.com/wiki/page/BGG_XML_API2

Note: the XML API does NOT require an API key. It does however throttle requests.
To address this, game data is fetched in batches of 100.

Note_2: the API must be queried via either game_id or game name.
There is no readily available list of all game_ids.
To address this, the module fetches 17,313 ids of games with more than 30 reviews from this data source:
https://raw.githubusercontent.com/beefsack/bgg-ranking-historicals/master/2019-07-08.csv

"""

import yaml
import sys
import json
import numpy as np
import pandas as pd
import argparse
import logging
import logging.config

from boardgamegeek import BGGClient
from boardgamegeek.exceptions import BGGApiError, BGGError, BGGItemNotFoundError, BGGValueError

logging_config = './config/logging/local.conf'

try: # Set Logging configurations from file
    logging.config.fileConfig(logging_config)
except: # Fallback to basic configurations
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)

# FUNCTIONS
def fetch_game_ids(url: str) -> list:
    """Retrieve game ids with more than 30 reviews from specified url

    Args:
        url (`str`): the url to retrieve data from
        Should be "https://raw.githubusercontent.com/beefsack/bgg-ranking-historicals/master/2019-07-08.csv"

    Returns:
        ids (`numpy.ndarray`): numpy array with game ids
    """
    df = pd.read_csv(url)
    ids = df['ID'].values
    return ids

def batch_api_call(ids: np.array, batch_size: int=100, requests_per_minute: int=100) -> list:
    """Fetches games data in batches

    First fetches data one batch at a time. Then fetches one more batch with remainder_ids
    i.e. ids which were left over after the last full batch was formed

    Args:
        ids (`numpy.array`): the game_ids to fetch data for
        batch_size (`int`): the size of the batches (Recommend to not exceed 100)
        requests_per_minute (`int`): limit the number of requests of our API client

    Returns:
        games (`list`): List of BoardGame objects. See boardgamegeek package documentation for details:
        https://lcosmin.github.io/boardgamegeek/modules.html#boardgamegeek.objects.games.BoardGame
    """

    # Instantiate API client
    bgg = BGGClient(requests_per_minute=requests_per_minute)
    logger.info(f'Instantiated API client with  limit of {requests_per_minute} requests per minute.')

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
    logger.info(f'Beginning batch calls to BoardGameGeek API for {batch_size} games per batch.')
    logger.info(f"This will take approximately 15 minutes. Thank you for your patience.")
    for batch in batches:
        logger.debug(f"Fetching data for batch number {batch_number} / {len(batches)}")
        try:
            game_batch = bgg.game_list(batch)
            batches_successful += 1
            logger.debug(f"Successfully fetched games in batch number {batch_number}")
            if batches_successful % 10 == 0:
                logger.info(f'Successfully fetched games for {batches_successful} batches')
            games.extend(game_batch)
        except BGGApiError:
            batches_failed += 1
            logger.debug(f"Failed to fetch games data for batch number {batch_number}")

        batch_number += 1

    logger.info(f"Successful Batches: {batches_successful} ")
    logger.info(f"Failed Batches: {batches_failed} ")

    # Fetch remaining games, which didn't fit in a batch
    remainder_ids = list(ids[len(ids_no_remainder):])
    remainder_ids_successful = 0
    remainder_ids_failed = 0
    try:
        games.extend(bgg.game_list(remainder_ids))
        logger.debug("Successfully fetched games with remainder ids")
        remainder_ids_successful = len(remainder_ids)
    except BGGApiError:
        logger.debug("Failed to fetch games with remainder ids")
        remainder_ids_failed = len(remainder_ids)


    logger.info(f"Total games successfully fetched: {batch_size*batches_successful+remainder_ids_successful}")
    logger.info(f"Total games failed to fetch: {batch_size * batches_failed+ remainder_ids_failed}")

    return games


def convert_game_to_dict(game) -> dict:
    """Extract all useful information from a game object and return as a dictionary

    Args:
        game (`BoardGame`): BoardGame object as defined in the boardgamegeek package
        See documentation for details: https://lcosmin.github.io/boardgamegeek/modules.html#boardgamegeek.objects.games.BoardGame

    Returns:
        dict_game (`dict`): A dictionary with relevant information about a game
    """
    dict_game = {}
    dict_game['id'] = game.id # Unique identifier for each game on the BoardGameGeek website
    dict_game['name'] = game.name # Game name
    dict_game['stats'] = game.stats # Game stats like avg. user rating, avg. complexity rating, etc.
    dict_game['image'] = game.image
    dict_game['thumbnail'] = game.thumbnail
    dict_game['artists'] = game.artists # Develop the artwork for the game (cards, box, miniatures, etc.)
    dict_game['designers'] = game.designers # The game designers that develop the mechanics of the game
    dict_game['year'] = game.year # Year the game was published
    dict_game['description'] = game.description
    dict_game['categories'] = game.categories # Categories the game falls under on the BoardGameGeek website
    dict_game['mechanics'] = game.mechanics # Mechanics present in the game as identified on BoardGameGeek.com
    dict_game['min_age'] = game.min_age # Minimum recommended age to play the game
    dict_game['publishers'] = game.publishers # The companies that publish the game (might be different in different countries/continents)

    return dict_game


if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Fetches up-to-date data on 17,313 games from BoardGameGeek.com")
    parser.add_argument('-c', '--config', help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml", default='../config/config.yml', type=str)
    parser.add_argument('-o', '--output', help="Path to output of games.json. Default: ../data/external/games.json", default="../data/external/games.json", type=str)
    # Parse CLI arguments
    args = parser.parse_args()

    # Load .yml config file
    try:
        with open(args.config, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logger.info(f'Loaded configurations from {args.config}')
    except FileNotFoundError as e:
        logger.error(f"Could not load configurations file, didn't find it at {args.config} and threw error {e}")
        logger.error('Terminating process prematurely')
        sys.exit()

    # Get the ids of 17,313 games
    ids = fetch_game_ids(**config['acquire']['fetch_game_ids'])
    # Fetch up-to-date data on these games from the BoardGameGeek XML API via the boardgamegeek wrapper
    # Expected time to completion: ~5 minutes. Time to stretch your legs or get some coffee!
    games = batch_api_call(ids, **config['acquire']['batch_api_call'])

    # Extract the relevant data from the BoardGame objects and convert it to dictionaries
    dict_games = []
    for game in games:
        try:
            dict_game = convert_game_to_dict(game)
            dict_games.append(dict_game)
        except:
            logging.debug(f"Failed to convert to dict game with id {game.id}")

    # Save results to json
    with open(args.output, 'w') as fp:
        json.dump(dict_games, fp)



