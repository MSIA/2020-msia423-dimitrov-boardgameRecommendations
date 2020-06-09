import json
import logging
import pandas as pd
import numpy as np
import yaml
import logging.config
import argparse
import sys
import pickle

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

logging_config = './config/logging/local.conf'
try:
    logging.config.fileConfig(logging_config)
except:
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)


def load_featurized_data(filepath: str) -> pd.DataFrame:
    """Loads json data from local filepath and returns a dictionary """
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            df = pd.DataFrame(data)
            logger.info(f'Successfully loaded unfeaturized data from {filepath}')
    except FileNotFoundError as e:
        logger.error(f'Did not find file at {filepath} and got error {e}')
        logger.error('Terminating process prematurely')
        sys.exit()

    return df


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Drops all columns, which are not relevant features for KMeans Clustering"""

    logger.debug('Dropping columns which are not relevant features for KMeans Clustering')
    try:
        features_df = df.drop(['id', 'name', 'image', 'thumbnail', 'artists', 'publishers',
                           'designers', 'description', 'categories', 'mechanics'], axis=1)
        return features_df
    except KeyError as e:
        logger.error(f'Did not find all the columns that are supposed to be drop and got error {e}. Check the schema?')
        logger.error('Returning original dataframe')
        return df


def standardize_features(df: pd.DataFrame) -> np.ndarray:
    """Standardize Feature Matrix. Takes pd.DataFrame and returns Numpy array"""

    logger.info('Standardizing Features')
    try:
        standardized_features = StandardScaler().fit_transform(df)
        return standardized_features
    except ValueError as e:
        logger.error(f'Encountered error: {e}. Maybe your dataframe is empty?')
        logger.error('Returning original dataframe')
        return df


def fit_kmeans(X: np.ndarray, k: int, seed: int):
    """Fits sklearn KMeans clustering algorithm with k clusters to training data X

    Args:
        X (`np.ndarray`): Training data for KMeans
        k (`int`): number of clusters for KMeans()
        seed (`int`): random_state for KMeans() to ensure reproducibility

    Returns:
        kmeans: sklearn transformer object to make predictions for new data based on KMeans algorithm
    """

    try:
        # Instantiate estimator
        kmeans = KMeans(n_clusters=k, random_state=seed)
        # Fit estimator on standardized feature data
        logger.info('Fitting KMeans Clustering algorithm to provided feature data. This will take ~2 minutes')
        kmeans.fit(X)
        return kmeans
    except ValueError as e:
        logger.error(f'Encountered error: {e}. Maybe you specified a seed, which is not a whole number?')
        logger.error('Terminating process prematurely')
        sys.exit()
    except TypeError as e:
        logger.error(f'Encountered error: {e}. Maybe you specified a value for n_clusters, which is not a whole number?')
        logger.error('Terminating process prematurely')
        sys.exit()


def model_predict(X, model):
    """Calculates labels for feature data based on provided model

    Args:
        X: Data to calculate clusters for with sklearn transformer object
        model: sklearn transformer object to be used for predictions

    Returns:
        model.labels_ : the labels predicted for X data
    """
    logger.info('Calculating labels (clusters) for provided data')
    model.predict(X)

    return model.labels_


def evaluate_silhouette(X, labels):
    """Calculate silhouette score for X data & clustered labels"""
    return silhouette_score(X, labels)


def combine_with_labels(df, labels):
    """Combining clustering labels with training data"""

    # Taking only the relevant columns and removing the ones with the one-hot encoded features
    cols_left = list(df.columns[:12]) + list(df.columns[-6:])
    df = df[cols_left]
    df['cluster'] = labels

    return df


if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Trains a KMeans Clustering algorithm and applies labels to featurized data in data/games_featurized.json")
    parser.add_argument('-i', '--input',
                        help="Path to input (games_featurized.json). Default: ../data/games_featurized.json",
                        default="../data/games_featurized.json", type=str)
    parser.add_argument('-c', '--config',
                        help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml",
                        default='../config/config.yml', type=str)
    parser.add_argument('-o', '--output',
                        help="Path to output labelled (clustered) data. Default: ../data/games_clustered.json",
                        default="../data/games_clustered.json", type=str)
    parser.add_argument('-mo', '--model_output',
                        help="Path to save trained model. Default: ../models/kmeans.pkl",
                        default="../models/kmeans.pkl", type=str)

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
    featurized_data = load_featurized_data(args.input)

    # Extract relevant feature columns
    features_df = extract_features(featurized_data)

    # Standardize data and return feature matrix (numpy array)
    X = standardize_features(features_df)

    # Fit KMeans model
    model = fit_kmeans(X, **config['model']['kmeans'])

    # Calculate labels for data
    labels = model_predict(X, model)

    # Calculate Silhouette score for fitted model and labels for the training data
    silhouette_score_ = evaluate_silhouette(X, labels)

    # Combining the original df with the labels and dropping unnecessary columns (now that the modelling is done)
    df = combine_with_labels(featurized_data, labels)

    # Converting back to dictionary so I can save as json
    df_dict = df.to_dict(orient='records')

    # Saving final json data, which will be used for upload to database
    with open(args.output, 'w') as fp:
        json.dump(df_dict, fp)
        logger.info(f'Saved final json data to {args.output}')

    # Saving calculated model
    with open(args.model_output, 'wb') as output:
        pickle.dump(model, output)
        logger.info(f'Saved model to {args.model_output}')
        logger.info('It might take ~30 seconds for the file to appear in your file system')

    # Saving silhouette score
    model_silhouette_path = args.model_output[:-4] + '.txt'  # Changing the file extension from .pkl to .txt
    with open(model_silhouette_path, "w") as text_file:
        text_file.write(f"The model silhouette score is: {silhouette_score_}")
        logger.info(f'Saved silhouette score to {model_silhouette_path}')