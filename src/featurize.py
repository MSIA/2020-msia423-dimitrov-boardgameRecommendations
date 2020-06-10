""" This module creates features from the unfeaturized json data

Overall, the data goes through 5 steps in order for a given feature to be properly one-hot encoded.
0. The dictionary data is converted to Pandas DataFrame
1. Each game is expanded out to multiple rows, such that each row contains just 1 category from the game's categories
2. Then the data gets one-hot encoded via pd.get_dummies()
3. We take only the columns with the one-hot encoded data with game_id as unique identifier and sum over columns to bring all the categories for a given game onto just 1 row
4. The aggregated one-hot encoded data is joined back with the original dataset

The above steps are performed once for categories and once for mechanics.
All the steps are combined into a wrapper function, which is called twice

Finally, the relevant data in the 'stats' dictionary is extracted and the stats column is dropped
"""

import argparse
import json
import logging
import logging.config
import sys

import numpy as np
import pandas as pd
import yaml

logging_config = './config/logging/local.conf'
try:
    logging.config.fileConfig(logging_config)
except:
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)


def load_unfeaturized_data(filepath: str) -> dict:
    """Loads json data from local filepath and returns a dictionary """
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            logger.info(f'Successfully loaded unfeaturized data from {filepath}')
    except FileNotFoundError as e:
        logger.error(f'Did not find file at {filepath} and got error {e}')
        logger.error('Terminating process prematurely')
        sys.exit()

    return data


# STEP 1 - expand the columns for a given feature
# Based on this SO post: # https://stackoverflow.com/questions/27263805/pandas-column-of-lists-create-a-row-for-each-list-element
def expand_feature(df: pd.DataFrame, feature_name: str) -> pd.DataFrame:
    """Expected input is a dataframe where the 'feature_name' column contains a list in each row
    This function 'unpacks' i.e. 'expands' that feature so that each element in the list is on a separate row

    Args:
        df (`pd.DataFrame`):
        feature_name (`str`): feature name to featurize (expect 'categories' or 'mechanics')

    Returns:
        df_expanded_feature (`pd.DataFrame`): Dataframe where each row contains 1 element and not a list in the 'feature_name' column
    """
    logger.debug(f'Expanding Features for {feature_name}')
    try:
        df_expanded_feature = pd.DataFrame({
            col: np.repeat(df[col].values, df[feature_name].str.len())
            for col in df.columns.drop(feature_name)}
        ).assign(**{feature_name: np.concatenate(df[feature_name].values)})[df.columns]
    except KeyError as e:
        logger.error(f'Did not find column "{feature_name}" in provided DataFrame and got error {e}')
        logger.error('Terminating process prematurely')
        sys.exit()

    return df_expanded_feature


# STEP 2 - get_dummies
# # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.get_dummies.html
def one_hot_encode(df: pd.DataFrame, feature_name: str) -> pd.DataFrame:
    """One-hot encodes selected feature in given dataframe

    Args:
        df (`pd.DataFrame`): The dataframe with 'feature_name' column that needs one-hot encoding
        feature_name (`str`): The name of the column (feature) to one-hot encode

    Returns:
        df_one_hoy_encoded (`pd.DataFrame`): DataFrame with 'feature_name' column one hot encoded
    """

    logger.debug(f'One hot encoding for {feature_name}')
    if 'id' not in df.columns:
        logger.warning('The dataframe does not contain the "Id" column.')
        logger.warning('It might not be possible to join the one-hot encoded data back with the original dataset')
    try:
        df_one_hot_encoded = pd.get_dummies(df, columns=[feature_name])
        logger.debug(f'Successfully one-hot encoded {feature_name} column')
    except (ValueError, KeyError) as e:
        logger.error(f'Could not one-hot encode the data and got error {e}. Maybe the dataframe is empty?')
        logger.error('Terminating process prematurely')
        sys.exit()

    return df_one_hot_encoded


# STEP 3
def collapse_one_hot_encoded(df: pd.DataFrame, index: int) -> pd.DataFrame:
    """Takes only the columns with the one-hot encoded data and
    collapses all the one hot encoded rows for a single game onto a single row

    Uses the index at which the one hot encoded columns start to separate out only those rows

    Args:
        df(`pd.DataFrame`):
        index (`int`): The index at which the one hot encoded columns start

    Returns:
        df_one_hot_collapsed (`pd.DataFrame`):
    """
    # Taking only the columns for the given feature and the id column so we can join back later
    logger.debug('Collapsing one hot encoded columns')

    id_and_feature_columns = ['id'] + list(df.columns[index:])

    # Collapsing the feature columns so all binary feature values are on the same row
    try:
        df_one_hot_collapsed = df[id_and_feature_columns].groupby(by='id', as_index=False).sum()
        return df_one_hot_collapsed
    except KeyError as e:
        logger.error(f'Cannot collapse one_hot_encoded columns. Is the "id" column in the dataframe?')
        logger.error('Terminating process prematurely')
        return df


# STEP 4
def merge_original_with_collapsed(df: pd.DataFrame, collapsed: pd.DataFrame) -> pd.DataFrame:
    """Merge 2 dataframes based on id column and return merged DataFrame"""

    logger.debug('Merging with original dataframe')
    try:
        df_with_feature = df.merge(collapsed, how='inner', on='id')
        return df_with_feature
    except KeyError as e:
        logger.error(f'Could not merge the two dataframes and got error {e}. Maybe the "id" column is missing from one of them> it is the key that is being used to join')
        logger.error('Terminating process prematurely')
        sys.exit()


# WRAPPER FUNCTION
def wrapper(df: pd.DataFrame, feature_name: str, index: int) -> pd.DataFrame:
    """ Wrapper for the 5 steps described above
    Args:
        df (`pd.DataFrame`): DataFrame to featurize
        feature_name (`str`): The feature to one-hot encode in a many-to-many context
        index (`int`): The column number at which the feature columns start (expect 12 for categories and 95 for mechanics)

    Returns:
        df_with_feature (`pd.DataFrame`): The original dataframe with one-hot encoded columns for all the values in the feature_name column
    """
    logger.info(f'Executing wrapper function for {feature_name}')
    # Step 1
    df_expanded_feature = expand_feature(df, feature_name)
    # Step 2
    df_one_hot_encoded = one_hot_encode(df_expanded_feature, feature_name)
    # Step 3
    df_one_hot_collapsed = collapse_one_hot_encoded(df_one_hot_encoded, index)
    # Step 4
    df_with_feature = merge_original_with_collapsed(df, df_one_hot_collapsed)

    logger.info(f'Completed wrapper function for {feature_name}')
    return df_with_feature


def extract_stats(df: pd.DataFrame) -> pd.DataFrame:
    """The 'stats' column in the df contains dictionaries
    This function extracts the relevant information from those dictionaries and drops the stats column

    Returns the DataFrame with the extracted columns and without the stats column
    """
    logger.debug('Extracting stats into new columns from the "stats" column, which contains dictionaries columns')
    try:
        df['number_of_user_ratings'] = df.apply(lambda row: row['stats']['usersrated'], axis=1)
        df['average_user_rating'] = df.apply(lambda row: row['stats']['average'], axis=1)
        df['number_of_user_weight_ratings'] = df.apply(lambda row: row['stats']['numweights'], axis=1)
        df['average_user_weight_rating'] = df.apply(lambda row: row['stats']['averageweight'], axis=1)
        df['bayes_average'] = df.apply(lambda row: row['stats']['bayesaverage'], axis=1)
        df['number_of_users_own'] = df.apply(lambda row: row['stats']['owned'], axis=1)
    except KeyError as e:
        logger.error(f'Could not extract relevant stats from "stats" column and got error: {e}')
        logger.error('Is the "stats" column in the dataframe?')
        logger.error('Returning original dataframe')
        return df

    logger.debug('Dropping stats column with dictionaries')
    df = df.drop('stats', axis=1)
    logger.info('Extracted stats into new columns')
    return df


if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Creates One-hot encoded features for categories and mechanics from data/games.json")
    parser.add_argument('-i', '--input',
                        help="Path to input (unfeaturized games.json). Default: ../data/games.json",
                        default="../data/games.json", type=str)
    parser.add_argument('-c', '--config',
                        help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml",
                        default='../config/config.yml', type=str)
    parser.add_argument('-o', '--output',
                        help="Path to output of games.json. Default: ../data/games_featurized.json",
                        default="../data/games_featurized.json", type=str)
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

    # Load unfeaturized json data into a dictionary
    unfeaturized_data = load_unfeaturized_data(args.input)

    # Step 0: Convert the unfeaturized data dictionary to pandas DataFrame
    df = pd.DataFrame(unfeaturized_data)

    # Calling wrapper function to create categories features
    featurized_categories_data = wrapper(df, 'categories', config['featurize']['index_categories'])

    # Calling wrapper function to create mechanics features
    featurized_mechanics_data = wrapper(featurized_categories_data, 'mechanics', config['featurize']['index_mechanics'])

    featurized_data = extract_stats(featurized_mechanics_data)

    # Converting back to dictionary so I can save as json
    df_dict = featurized_data.to_dict(orient='records')

    # Save results to json
    with open(args.output, 'w') as fp:
        json.dump(df_dict, fp)
        logger.info(f'Successfully saved featurized data to {fp}')