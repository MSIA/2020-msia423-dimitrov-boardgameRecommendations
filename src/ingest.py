'''This module ingests data from a local file into a database

That database can either be a local SQLite or an AWS RDS MYSQL Instance.

'''

import yaml
import json
from json import JSONDecodeError
import numpy as np
import pandas as pd
import argparse
import logging
import logging.config

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InterfaceError, IntegrityError, ProgrammingError
from sqlalchemy.ext.declarative import declarative_base

from config.flaskconfig import SQLALCHEMY_DATABASE_URI

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
        logger.error(f"Expected games to be a list; instead received type: {type(records)}. Returning None")
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

##############################
######### CREATE DB ##########
##############################

def create_db(args):
    """Create table inside a database and create DB if it doesn't exist"""

    # Define Engine
    engine = create_engine(args.engine_string)
    # Create Database
    Base.metadata.create_all(engine)

def get_session(engine=None, engine_string=None):
    """Returns a session to the provided SQL database

    Args:
        engine_string: SQLAlchemy connection string in the form of:

    Returns:
        SQLAlchemy session
    """

    if engine is None and engine_string is None:
        return ValueError("`engine` or `engine_string` must be provided")
    elif engine is None:
        engine = create_connection(engine_string=engine_string)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session

##############################
####### INGEST TO DB #########
##############################

def ingest(args):
    """ Ingests games via session to a database"""
    # Parsing arguments from command line: filepath of data to be ingested & session to use for ingesting
    try:
        with open(args.local_filepath) as json_file:
            games=json.load(json_file)
    except JSONDecodeError:
        logger.error(f'Failed to open {args.local_filepath}. Not a valid JSON file')

    session=get_session(args.engine_string)

    # Check if games is a list
    if type(games) != list:
        logger.error(f"Expected games to be a list; instead received type: {type(games)}. Returning None")
        return None

    logger.info(f"Persisting {len(games)} games to {session.connection().engine}")
    successfully_added = 0
    not_added = 0
    for game in games:
        try:
            # Define a boardgame in the ORM
            boardgame = Boardgame(game_id=game['id'],
                                 name=game['name'],
                                 image=game['image'],
                                 thumbnail = game['thumbnail'],
                                 description=game['description'],
                                 year_published=date(year=game['year'], month=1, day=1 ),
                                 min_age=game['min_age'],
                                 number_of_ratings=game['stats']['usersrated'],
                                 average_user_rating=game['stats']['average'],
                                 number_of_ratings_weight=game['stats']['numweights'],
                                 average_user_rating_weight=game['stats']['averageweight'],
                                 bayes_average=game['stats']['bayesaverage'])
            session.add(boardgame)
            successfully_added += 1
        except ProgrammingError as err:
            not_added += 1
            logger.error('''Programming Error; possible reasons:
                                    table not found or already exists,
                                    syntax error in the SQL statement,
                                    wrong number of parameters specified, etc.''')
            logger.debug(
                f"Error: {err}; game_id: {game['game_id']}, name: {game['name']} couldn't be added to session")
        except IntegrityError as err:
            not_added += 1
            logger.error("Relational integrity of the database affected e.g. foreign key check fails")
            logger.debug(
                f"Error: {err}; game_id: {game['game_id']}, name: {game['name']} couldn't be added to session")
        except InterfaceError as err:
            not_added += 1
            logger.error(
                '''InterfaceError: sometimes raised by drivers in the context of the database connection being dropped, 
                    or not being able to connect to the database.''')
            logger.debug(
                f"Error: {err}; game_id: {game['game_id']}, name: {game['name']} couldn't be added to session")

    logger.info(f"Successfully added to session {successfully_added} sentiment records")
    logger.info(f"Failed to add to session {not_added} sentiment records")

    for game in games:
        continue
    pass

if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Create and/or ingest data into database")
    subparsers = parser.add_subparsers()

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sb_create.set_defaults(func=create_db)

    # Sub-parser for ingesting new data
    sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    sb_ingest.add_argument("-lfp","--local_filepath", default="../data/games.json", help="Path to json data to be ingested into database")
    sb_ingest.add_argument("--engine_string", default='sqlite:///data/tracks.db',
                           help="SQLAlchemy connection URI for database")
    sb_ingest.set_defaults(func=ingest)

    args = parser.parse_args()
    args.func(args)