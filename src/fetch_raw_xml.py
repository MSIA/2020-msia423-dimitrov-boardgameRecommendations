"""
This module loads game_ids from a .txt file
then uses those ids to retrieve raw XML data from BoardGameGeek.com via their XML API2
API Documentation: https://boardgamegeek.com/wiki/page/BGG_XML_API2
"""

import logging
import sys
import logging.config
import argparse
import requests
import xml.etree.ElementTree as ET

logging_config = './config/logging/local.conf'

try: # Set Logging configurations from file
    logging.config.fileConfig(logging_config)
except: # Fallback to basic configurations
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)


def load_txt(filepath: str) -> list:
    """Loads a .txt file and returns contents as a list of integers"""

    try:
        with open(filepath, 'r') as f:
            game_ids = [int(line.rstrip('\n')) for line in f]
            logger.debug(f'Successfully loaded game_ids from {filepath} and returned them as list of integers')
            return game_ids
    except FileNotFoundError as e:
        logger.error(f"Invalid path or didn't find game_ids at specified path; Got error: {e}")
        logger.error('Terminating process prematurely')
        sys.exit()


def call_xml_api(game_id: int):
    """Query the BoardGameGeek XML API for a game_id

    Args:
        game_id (`int`): the unique game_id used to query raw XML data for that game from BoardGameGeek XML API

    Returns:
        root: XML root object
    """
    url = "https://www.boardgamegeek.com/xmlapi2/thing?"
    payload = {"id": game_id}
    bggResponse = requests.get(url, params=payload)
    root = ET.fromstring(bggResponse.text)

    return root


if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Fetches up-to-date data on 17,313 games from BoardGameGeek.com")
    parser.add_argument('-i', '--input', help="Path to output of games.json. Default: ./data/game_ids.txt", default="./data/game_ids.txt", type=str)
    parser.add_argument('-o', '--output', help="Path to output of games.json. Default: ./data/raw_data.xml", default="./data/raw_data.xml", type=str)

    # Parse CLI arguments
    args = parser.parse_args()

    # Read in game_ids
    game_ids = load_txt(args.input)

    # Initialize XML root with first game_id on the list
    # (I'm not exactly sure how to work with these XML objects, but initializing the list with the first game_id
    # and then appending to that works)
    logger.debug('Calling XML API for first element in game_ids')
    root_start = call_xml_api(game_ids[0])

    # Go over the remaining game_ids and append to the XML root
    counter = 0
    logger.info("Beginning calls to XML API for all game_ids (except the first one).")
    logger.info("This will take ~20 minutes. Thank you for your patience.")
    for game_id in game_ids[1:]:
        logger.debug(f'Calling XML API for game_id: {game_id}')
        # time.sleep(.1)
        root = call_xml_api(game_id)
        root_start.append(root)
        counter += 1
        if counter % 500 == 0:
            logger.info(f'Collected XML response for {counter} games')

    # Convert XML root to tree and write to file
    tree = ET.ElementTree(root_start)
    tree.write(args.output)
    logger.info(f'Successfully wrote the raw XML data from BoardGameGeek XML API to {args.output}')