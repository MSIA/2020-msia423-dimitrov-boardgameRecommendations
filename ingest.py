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
import sys

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InterfaceError, IntegrityError, ProgrammingError
from sqlalchemy.ext.declarative import declarative_base

from config.flaskconfig import SQLALCHEMY_DATABASE_URI

Base = declarative_base()
logging_config='config/logging/local.conf'
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

    # Need to add collation argument for two of the columns to avoid odd warnings when uploading to MySQL in RDS
    # Those warnings are most likely related to UTF-8 characters which need 4 instead of 3 bytes to be stored.
    # SQLAlchemy Documentation: https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.String.__init__
    # MySQL Documentation: https://dev.mysql.com/doc/refman/8.0/en/charset-unicode-utf8mb4.html
    # StackOverflow Thread: https://stackoverflow.com/questions/10957238/incorrect-string-value-when-trying-to-insert-utf-8-into-mysql-via-jdbc

    game_id = Column(String(100), primary_key=True, unique=True, nullable=False)
    name = Column(String(200), unique=False, nullable=False) # Collation Needed
    image = Column(String(150), unique=False, nullable=True)
    thumbnail = Column(String(100), unique=False, nullable=True)
    description = Column(Text, unique=False, nullable=True) # Collation Needed
    year_published = Column(Integer, unique=False, nullable=True)
    min_age = Column(Integer, unique=False, nullable=True)
    number_of_ratings = Column(Integer, unique=False, nullable=True)
    average_user_rating = Column(Float, unique=False, nullable=True)
    number_of_ratings_weight = Column(Integer, unique=False, nullable=True)
    average_user_rating_weight = Column(Float, unique=False, nullable=True)
    bayes_average = Column(Float, unique=False, nullable=True)
    number_of_users_own = Column(Integer, unique=False, nullable=True)
    cluster = Column(Integer, unique=False, nullable=True)

    def __repr__(self):
        game_repr = f"<Boardgame(game_id={self.game_id}, name={self.name})>"
        return game_repr

##############################
######### VALIDATION #########
##############################

def validate(games: list) -> list:
    """This function validates boardgames before they are ingested"""

    expected_schema = {'id', 'name', 'image', 'thumbnail', 'artists', 'designers', 'year', 'description', 'categories',
                       'mechanics', 'min_age', 'publishers', 'number_of_user_weight_ratings', 'average_user_weight_rating',
                       'number_of_user_ratings', 'average_user_rating', 'bayes_average', 'number_of_users_own', 'cluster'}
    unexpected_schema_count=0
    invalid_game_id=0
    missing_name=0
    validated_games = []

    # Check if games is a list
    if type(games) != list:
        logger.error(f"Expected games to be a list; instead received type: {type(games)}. Returning None")
        return None

    logger.info(f'Validating {len(games)} games')
    for game in games:

        # Check if game schema is valid
        if game.keys() != expected_schema:
            logger.debug(f"Encountered a game, which doesn't match expected schema")
            unexpected_schema_count += 1
            continue

        try: # Check if game_id exists and is a valid entry
            float(game['id'])  # Using float, because int memory might not be enough
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

    logger.info(f'{len(validated_games)} games passed validation checks')

    return validated_games

##############################
######### CREATE DB ##########
##############################

def create_db(args):
    """Create a DB if it doesn't exist and a table inside based on the defined SQLAlchemy ORM"""

    # Define Engine
    logger.debug(f'Creating engine from Engine String')
    engine = create_engine(args.engine_string)
    # Create Database
    Base.metadata.create_all(engine)

def get_session(engine_string=None):
    """Returns a session to the provided SQL database

    Args:
        engine_string: SQLAlchemy connection string in the form of:

    Returns:
        SQLAlchemy session
    """
    logger.debug(f'Creating engine from Engine_string')
    engine = create_engine(engine_string)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def _truncate_boardgames(session):
    """Deletes all entries in boardgames table if rerunning and run into unique key error."""
    session.execute('''DELETE FROM boardgames''')

##############################
####### INGEST TO DB #########
##############################

def ingest(args):
    """ Ingests games via session to a database"""
    # Parsing arguments from command line: filepath of data to be ingested & session to use for ingesting
    try:
        with open(args.local_filepath) as json_file:
            games=json.load(json_file)
            logger.info(f"Successfully loaded data from {json_file.name}")
    except JSONDecodeError:
        logger.error(f'Failed to open {args.local_filepath}. Not a valid JSON file')

    logger.debug(f'Creating Session to DB Engine String: {args.engine_string}')
    session=get_session(engine_string=args.engine_string)

    # Use the validate() function from above to check input
    games=validate(games)

    # Check if games is a list
    if type(games) != list:
        logger.error(f"Expected games to be a list; instead received type: {type(games)}. Returning None")
        return None

    logger.info(f"Persisting {len(games)} games to database")
    logger.info(f"This will take approximately 15 minutes. Thank you for your patience.")
    successfully_added = 0
    not_added = 0
    for game in games:
        try:
            # Define a boardgame in the ORM
            boardgame = Boardgame(game_id=str(game['id']),
                                  name=game['name'],
                                  image=game['image'],
                                  thumbnail = game['thumbnail'],
                                  description=game['description'],
                                  year_published=game['year'],
                                  min_age=game['min_age'],
                                  number_of_ratings=game['number_of_user_ratings'],
                                  average_user_rating=game['average_user_rating'],
                                  number_of_ratings_weight=game['number_of_user_weight_ratings'],
                                  average_user_rating_weight=game['average_user_weight_rating'],
                                  bayes_average=game['bayes_average'],
                                  number_of_users_own=game['number_of_users_own'],
                                  cluster=game['cluster'])
            session.add(boardgame)
            successfully_added += 1

            # Commit batches of 100 games
            if successfully_added % 100 == 0:
                session.commit()

            if successfully_added % 1000 == 0:
                logger.info(f"Successfully persisted {successfully_added} boardgames")

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
            logger.error("Relational integrity of the database affected e.g. Primary key uniqueness or foreign key check fails")
            logger.debug(f"Error: {err}; game_id: {game['id']}, name: {game['name']} couldn't be added to session")
        except InterfaceError as err:
            not_added += 1
            logger.error(
                '''InterfaceError: sometimes raised by drivers in the context of the database connection being dropped, 
                    or not being able to connect to the database.''')
            logger.debug(
                f"Error: {err}; game_id: {game['game_id']}, name: {game['name']} couldn't be added to session")

    # Adding any remaining sessions, which were not in a batch of 100 records
    session.commit()

    logger.info(f"Successfully added to session {successfully_added} games")
    logger.info(f"Failed to add to session {not_added} games")
    session.close()

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
    sb_ingest.add_argument("-lfp","--local_filepath", default="./data/games_clustered.json", help="Path to json data to be ingested into database")
    sb_ingest.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")
    sb_ingest.add_argument("-t", "--truncate", default=False, action="store_true",
                        help="If given, delete current records from boardgames table before ingesting new data "
                             "so that table can be recreated without unique id issues ")
    sb_ingest.set_defaults(func=ingest)

    args = parser.parse_args()

    # Avoid error when using the create_db sub command
    try:
        if args.truncate:
            session = get_session(engine_string=args.engine_string)
            try:
                logger.info("Attempting to truncate boardgames table.")
                _truncate_boardgames(session)
                session.commit()
                logger.info("boardgames table truncated.")
            except Exception as e:
                logger.error("Error occurred while attempting to truncate boardgames table.")
                logger.error(e)
            finally:
                session.close()
    except AttributeError:
        pass

    args.func(args)