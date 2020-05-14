"""This module uploads a file to an s3 bucket

You can pass the local filepath of the file you want to upload via the [-lfp --local_filepath] optional command line argument
Otherwise default: data/external/games.json
"""

import boto3
import argparse
import logging
import logging.config
import yaml

# todo: Exception Handling

logging_config = './config/logging/local.conf'
try:
    logging.config.fileConfig(logging_config)
except:
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
logger = logging.getLogger('upload.py')

def upload_file_to_bucket(bucket_name, local_filepath, key):
    '''Upload file to S3 bucket with specified key

    Args:
        bucket_name (`str`): The S3 bucket to upload to
        local_filepath (`str`): The location of the file to be uploaded
        key (`str`): The name of the file on S3
    '''
    # Connect to S3
    s3 = boto3.resource('s3')
    logger.debug('Connected to S3')
    # Connect to Bucket # Note that all buckets have unique names so we don't need the 's3://' part
    bucket = s3.Bucket(bucket_name)
    logger.debug(f'Connected to {bucket_name}')
    # Upload to Bucket
    try:
        bucket.upload_file(local_filepath, key)
        logger.info(f'Successfully uploaded {local_filepath}')
    except Exception as err:
        logger.error(f'Failed to upload {local_filepath} with error: {err}')

if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Uploads a file to an S3 bucket")
    parser.add_argument('-c', '--config',
                        help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml",
                        default='../config/config.yml', type=str)
    parser.add_argument('-lfp', '--local_filepath', help="Local file path of file you want to upload. Default: ../data/external/games.json",
                        default="../data/external/games.json", type=str)
    # Parse command line arguments
    args = parser.parse_args()

    # Load .yml config file
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info(f'Configuration file loaded from {args.config}')

    # Upload file to S3 bucket
    try:
        upload_file_to_bucket(local_filepath=args.local_filepath, **config['upload'])
        logger.info(f'Successfully uploaded {args.local_filepath} to S3 bucket')
    except Exception as err: # Otherwise, rely on the config/config.yml file
        logger.error(f'Failed to upload {args.local_filepath} to S3 bucket with error: {err}')