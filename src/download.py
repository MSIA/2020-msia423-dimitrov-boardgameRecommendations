"""This module downloads a file from an s3 bucket

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