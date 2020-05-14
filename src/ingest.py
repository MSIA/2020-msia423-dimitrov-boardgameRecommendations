'''This module ingests data from a local file into a database

That database can either be a local SQLite or an AWS RDS MYSQL Instance.

'''

import yaml
import json
import numpy as np
import pandas as pd
import argparse
import logging
import logging.config

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

try: # Set Logging configurations from file
    logging.config.fileConfig(logging_config)
except: # Fallback to basic configurations
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)

# Defining Table Schema
class Boardgame(Base):
    """ Defines the data model for the table `boardgames`. """

    __tablename__ = 'boardgames'

    game_id = Column(String(100), primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=False, nullable=False)
    image = Column(String(150), unique=False, nullable=True)
    thumbnail = Column(String(100), unique=False, nullable=True)
    description = Column(Text, unique=False, nullable=True)
    year_published = Column(Date, unique=False, nullable=True)
    min_age = Column(Integer, unique=False, nullable=True)
    number_of_ratings = Column(Integer, unique=False, nullable=True)
    average_user_rating = Column(Float, unique=False, nullable=True)
    number_of_ratings_weight = Column(Integer, unique=False, nullable=True)
    average_user_rating_weight = Column(Float, unique=False, nullable=True)
    bayes_average = Column(Float, unique=False, nullable=True)

    def __repr__(self):
        game_repr = f"<Boardgame(game_id={self.game_id}, name={self.name})>"
        return game_repr

##############################
######### VALIDATION #########
##############################

def validate(games: list) -> list:
    """This function validates boardgames before they are ingested"""

    expected_schema = {'id', 'name', 'stats', 'image', 'thumbnail', 'artists', 'designers', 'year', 'description', 'categories', 'mechanics', 'min_age', 'publishers'}
    unexpected_schema_count=0
    invalid_game_id=0
    missing_name=0
    validated_games = []

    # Check if games is a list
    if type(games) != list:
        logger.error(f"Expected records to be a list; instead received type: {type(records)}. Returning None")
        return None

    for game in games:

        # Check if game schema is valid
        if game.keys() != expected_schema:
            logger.debug(f"Encountered a game, which doesn't match expected schema")
            unexpected_schema_count += 1
            continue

        try: # Check if game_id exists and is a valid entry
            float(game['game_id'])  # Using float, because int memory might not be enough
        except ValueError:
            logger.debug(f"Encountered a game with invalid game_id")
            invalid_game_id += 1
            continue
        except (KeyError, TypeError):
            logger.debug(f"Encountered a game with missing game_id")
            invalid_game_id += 1
            continue

        try: # Check if game name exists
            game['name']
        except KeyError:
            logger.debug(f"Encountered a game, which doesn't have a name")
            missing_name += 1
            continue

        # game passes validation checks
        validated_games.append(game)

    # log number of games with unexpected schemas
    if unexpected_schema_count != 0:
        logger.info(f"{unexpected_schema_count} game(s) with unexpected schema not added")
    else:
        logger.info("No games with unexpected schemas detected")

    # log number of games with invalid game ids
    if invalid_game_id != 0:
        logger.info(f"{invalid_game_id} game(s) with invalid id not added")
    else:
        logger.info("No games with invalid game ids found")

    # log number of games with missing names
    if missing_name != 0:
        logger.info(f"{missing_name} game(s) missing a name")
    else:
        logger.info("No games with missing names detected")

    return validated_games

def ingest(games):
    pass

if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Ingest local json file into database")
