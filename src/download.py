"""This module downloads a file from an s3 bucket

You can pass the local filepath of the file you want to upload via the [-lfp --local_filepath] optional command line argument
Otherwise default: data/external/games.json
"""

import boto3
from botocore.exceptions import ClientError
import argparse
import logging
import logging.config
import yaml
import sys

# todo: Exception Handling

logging_config = './config/logging/local.conf'
try:
    logging.config.fileConfig(logging_config)
except:
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger(__file__)

def download_file_from_bucket(bucket_name, key, local_filepath,):
    '''Download file from S3 bucket with specified key & filepath

    Args:
        bucket_name (`str`): The S3 bucket to download from
        key (`str`): The name of the file on S3
        local_filepath (`str`): The path to download the file to
    '''
    # Connect to S3
    s3 = boto3.resource('s3')
    logger.debug('Connected to S3')
    # Connect to Bucket # Note that all buckets have unique names so we don't need the 's3://' part
    bucket = s3.Bucket(bucket_name)
    logger.debug(f'Connected to {bucket_name}')
    # Download to Bucket
    try:
        bucket.download_file(key, local_filepath)
        logger.info(f'Successfully downloaded {key}')
    except ClientError as e:
        logger.error(f"Failed to download {key} with error: {e}. Maybe you didn't specify the file key correctly?")
        logger.error('Terminating process prematurely')
        sys.exit()
    except bucket.meta.client.exceptions.NoSuchKey:
        logger.error(f"Failed to download {key} with error: {e}. Maybe you didn't specify the file key correctly?")
        logger.error('Terminating process prematurely')
        sys.exit()
    except bucket.meta.client.exceptions.NoSuchBucket:
        logger.error(f"Failed to download {key} with error: {e}. Maybe you didn't specify the bucket name correctly?")
        logger.error('Terminating process prematurely')
        sys.exit()

if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Downloads a file from an S3 bucket")
    parser.add_argument('-c', '--config',
                        help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml",
                        default='../config/config.yml', type=str)
    parser.add_argument('-lfp', '--local_filepath',
                        help="Filepath for downloaded file. Default: ../data/games.json",
                        default="../data/games.json", type=str)
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
    download_file_from_bucket(local_filepath=args.local_filepath, **config['download'])
    logger.info(f'Successfully downloaded {config["download"]["key"]} from S3 bucket')