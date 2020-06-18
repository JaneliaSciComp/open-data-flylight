''' denormalize_s3.py
    Denormalize an S3 bucket (with a Template/Library prefix).
    A file named keys_denormalized.json is created in the Library.
'''

import argparse
import json
import sys
import colorlog
import boto3
from botocore.exceptions import ClientError
import requests

__version__ = '1.1.0'
# Configuration
CONFIG = {'config': {'url': 'http://config.int.janelia.org/'}}
AWS = dict()
KEYFILE = "keys_denormalized.json"


def call_responder(server, endpoint):
    """ Call a responder
        Keyword arguments:
        server: server
        endpoint: REST endpoint
    """
    url = CONFIG[server]['url'] + endpoint
    try:
        req = requests.get(url)
    except requests.exceptions.RequestException as err:
        LOGGER.critical(err)
        sys.exit(-1)
    if req.status_code != 200:
        LOGGER.error('Status: %s (%s)', str(req.status_code), url)
        sys.exit(-1)
    return req.json()


def initialize_program():
    """ Initialize
    """
    global AWS, CONFIG # pylint: disable=W0603
    data = call_responder('config', 'config/rest_services')
    CONFIG = data['config']
    data = call_responder('config', 'config/aws')
    AWS = data['config']


def get_all_s3_objects(s3c, **base_kwargs):
    """ Generator function to handle >1000 objects
        Keyword arguments:
          s3c: S# client instance
          base_kwargs: arguments for list_objects_v2
    """
    continuation_token = None
    while True:
        list_kwargs = dict(MaxKeys=1000, **base_kwargs)
        if continuation_token:
            list_kwargs['ContinuationToken'] = continuation_token
        response = s3c.list_objects_v2(**list_kwargs)
        yield from response.get('Contents', [])
        if not response.get('IsTruncated'):
            break
        continuation_token = response.get('NextContinuationToken')


def denormalize():
    """ Denormalize a buckek into a JSON file
        Keyword arguments:
          None
        Returns:
          None
    """
    #pylint: disable=no-member
    total_objects = 0
    sts_client = boto3.client('sts')
    aro = sts_client.assume_role(RoleArn=AWS['role_arn'],
                                 RoleSessionName="AssumeRoleSession1")
    credentials = aro['Credentials']
    s3_client = boto3.client('s3',
                             aws_access_key_id=credentials['AccessKeyId'],
                             aws_secret_access_key=credentials['SecretAccessKey'],
                             aws_session_token=credentials['SessionToken'])
    s3_resource = boto3.resource('s3',
                                 aws_access_key_id=credentials['AccessKeyId'],
                                 aws_secret_access_key=credentials['SecretAccessKey'],
                                 aws_session_token=credentials['SessionToken'])
    prefix = '/'.join([ARG.TEMPLATE, ARG.LIBRARY]) + '/'
    key_list = list()
    for obj in get_all_s3_objects(s3_client, Bucket=ARG.BUCKET, Prefix=prefix):
        if KEYFILE not in obj['Key']:
            total_objects += 1
            key_list.append(obj['Key'])
    object_name = '/'.join([ARG.TEMPLATE, ARG.LIBRARY, KEYFILE])
    tags = 'PROJECT=CDCS&STAGE=prod&DEVELOPER=svirskasr&VERSION=%s' % (__version__)
    LOGGER.info("Uploading %s", object_name)
    try:
        bucket = s3_resource.Bucket(ARG.BUCKET)
        bucket.put_object(Body=json.dumps(key_list, indent=4),
                          Key=object_name,
                          ACL='public-read',
                          ContentType='application/json',
                          Tagging=tags)
    except ClientError as err:
        LOGGER.error(str(err))
    print("Objects: %d" % total_objects)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Find bucket size")
    PARSER.add_argument('--bucket', dest='BUCKET', action='store',
                        default='janelia-flylight-color-depth', help='AWS S3 bucket')
    PARSER.add_argument('--template', dest='TEMPLATE', action='store',
                        default='JRC2018_Unisex_20x_HR', help='Template')
    PARSER.add_argument('--library', dest='LIBRARY', action='store',
                        default='Vienna_Gen1_LexA', help='Library')
    PARSER.add_argument('--verbose', dest='VERBOSE', action='store_true',
                        default=False, help='Flag, Chatty')
    PARSER.add_argument('--debug', dest='DEBUG', action='store_true',
                        default=False, help='Flag, Very chatty')
    ARG = PARSER.parse_args()
    LOGGER = colorlog.getLogger()
    if ARG.DEBUG:
        LOGGER.setLevel(colorlog.colorlog.logging.DEBUG)
    elif ARG.VERBOSE:
        LOGGER.setLevel(colorlog.colorlog.logging.INFO)
    else:
        LOGGER.setLevel(colorlog.colorlog.logging.WARNING)
    HANDLER = colorlog.StreamHandler()
    HANDLER.setFormatter(colorlog.ColoredFormatter())
    LOGGER.addHandler(HANDLER)
    initialize_program()
    denormalize()
