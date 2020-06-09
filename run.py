""" This module combines steps from download.py, featurize.py, and model.py
so that the model pipeline can be executed with a single docker run command.

Data is downloaded from S3 bucket, features are created,
and finally a KMeans algorithm is fit, generates labels, and is evaluated.
"""

import logging
import logging.config
import argparse
import yaml
import sys
import pandas as pd
import json
import pickle

import src.download as dl
import src.featurize as ft
import src.model as md

logging_config = './config/logging/local.conf'

try: # Set Logging configurations from file
    logging.config.fileConfig(logging_config, disable_existing_loggers=False)
except: # Fallback to basic configurations
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)


if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(
        description="Downloads raw data from S3, creates featurized data from it and finally trains a KMeans model, which is evaluated and saved as .pkl")
    parser.add_argument('-lfp', '--local_filepath',
                        help="Filepath for downloaded file. Default: ../data/games.json",
                        default="../data/games.json", type=str)
    parser.add_argument('-c', '--config',
                        help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml",
                        default='../config/config.yml', type=str)
    parser.add_argument('-o', '--output',
                        help="Path to output labelled (clustered) data. Default: ../data/games_clustered.json",
                        default="../data/games_clustered.json", type=str)
    parser.add_argument('-mo', '--model_output',
                        help="Path to save trained model. Default: ../models/kmeans.pkl",
                        default="../models/kmeans.pkl", type=str)

    # Parse command line arguments
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

    # Download file to S3 bucket
    try:
        dl.download_file_from_bucket(local_filepath=args.local_filepath, **config['download'])
        logger.info(f'Successfully downloaded {config["download"]["key"]} from S3 bucket')
    except Exception as err:  # Otherwise, rely on the config/config.yml file
        logger.error(f'Failed to download {config["download"]["key"]} from S3 bucket with error: {err}')

    # Load unfeaturized json data into a dictionary
    unfeaturized_data = ft.load_unfeaturized_data(args.local_filepath)

    # Convert the unfeaturized data dictionary to pandas DataFrame
    df = pd.DataFrame(unfeaturized_data)

    # Calling wrapper function to create categories features
    featurized_categories_data = ft.wrapper(df, 'categories', config['featurize']['index_categories'])

    # Calling wrapper function to create mechanics features
    featurized_mechanics_data = ft.wrapper(featurized_categories_data, 'mechanics', config['featurize']['index_mechanics'])

    # Extract relevant information from the 'stats' column (which contains dictionaries) into new columns, then drop it
    featurized_data = ft.extract_stats(featurized_mechanics_data)

    # Extract relevant feature columns for modelling
    features_df = md.extract_features(featurized_data)

    # Standardize data and return feature matrix (numpy array)
    X = md.standardize_features(features_df)

    # Fit KMeans model
    model = md.fit_kmeans(X, **config['model']['kmeans'])

    # Calculate labels for data
    labels = md.model_predict(X, model)

    # Calculate Silhouette score for fitted model and labels for the training data
    silhouette_score_ = md.evaluate_silhouette(X, labels)

    # Combining the original df with the labels and dropping unnecessary columns (now that the modelling is done)
    df = md.combine_with_labels(featurized_data, labels)

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

    # Saving silhouette score
    model_silhouette_path = args.model_output[:-4] + '.txt'  # Changing the file extension from .pkl to .txt
    with open(model_silhouette_path, "w") as text_file:
        text_file.write(f"The model silhouette score is: {silhouette_score_}")
        logger.info(f'Saved silhouette score to {model_silhouette_path}')