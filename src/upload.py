"""This module uploads data to an s3 bucket

You can pass the local filepath of the file you want to upload via the [-lfp --local_filepath optional command line argument
Alternatively, you can set the path in the config/config.yml file.

"""

import boto3
import argparse
import logging
import logging.config

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
    # Connect to S3
    s3 = boto3.resource('s3')
    # Connect to Bucket # Note that all buckets have unique names so we don't need the 's3://' part
    bucket = s3.Bucket(bucket_name, local_filepath)
    # Upload to Bucket
    bucket.upload_file(local_filepath, key)

if __name__ == "__main__":
    # Setup CLI argument parser
    parser = argparse.ArgumentParser(description="Fetches up-to-date data on 17,313 games from BoardGameGeek.com")
    parser.add_argument('-bm','--bucket_name', help="Name of the S3 bucket you want to upload to. Default: ")
    parser.add_argument('-c', '--config',
                        help="Path to .yml (YAML) config file with module settings. Default: ../config/config.yml",
                        default='../config/config.yml', type=str)
    parser.add_argument('-lfp', '--local_filepath', help="Local file path of file you want to upload. Default: ../data/external/games.json",
                        default="../data/external/games.json", type=str)

    args = parser.parse_args()

    # Load .yml config file
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info(f'Configuration file loaded from {args.config}')

    if args.local_filepath:
        upload_file_to_bucket(local_filepath=args.local_filepath, **config['upload'])
    else:
        upload_file_to_bucket(**config['upload'])