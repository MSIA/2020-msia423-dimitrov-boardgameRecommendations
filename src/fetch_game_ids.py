'''This module fetches game_ids from beefsack's GitHub
These are essential for querying the BoardGameGeek XML API2.
Link: https://github.com/beefsack/bgg-ranking-historicals/blob/master/2019-07-08.csv
'''

import pandas as pd
import yaml
import logging
import logging.config
import argparse

logging_config = './config/logging/local.conf'

try: # Set Logging configurations from file
    logging.config.fileConfig(logging_config)
except: # Fallback to basic configurations
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)


if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Fetches up-to-date data on 17,313 games from BoardGameGeek.com")
    parser.add_argument('-c', '--config', help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml", default='../config/config.yml', type=str)
    parser.add_argument('-o', '--output', help="Path to output of game_ids.txt. Default: ./data/game_ids.txt", default="./data/game_ids.txt", type=str)

    # Parse CLI arguments
    args = parser.parse_args()

    # Load .yml config file
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Define GitHub url based on config/config.yml
    url = config['acquire']['fetch_game_ids']['url']
    # Download game_ids from GitHub
    df = pd.read_csv(url)
    game_ids = df['ID'].values

    # Save game_ids to .txt file
    with open(args.output, 'w') as file:
        for game_id in game_ids:
            file.write("%i\n" % game_id)