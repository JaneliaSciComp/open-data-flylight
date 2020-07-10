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
COUNTFILE = "counts_denormalized.json"
TAGS = 'PROJECT=CDCS&STAGE=prod&DEVELOPER=svirskasr&VERSION=%s' % (__version__)


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


def upload_to_aws(s3r, body, object_name):
    """ Upload a file ro AWS S3
        Keyword arguments:
          s3r: S3 resource
          body: JSON
          object_name: object
        Returns:
          None
    """
    if ARG.TEST:
        LOGGER.info("Would have uploaded %s", object_name)
        return
    LOGGER.info("Uploading %s", object_name)
    try:
        bucket = s3r.Bucket(ARG.BUCKET)
        bucket.put_object(Body=body,
                          Key=object_name,
                          ACL='public-read',
                          ContentType='application/json',
                          Tagging=TAGS)
    except ClientError as err:
        LOGGER.error(str(err))


def denormalize():
    """ Denormalize a buckek into a JSON file
        Keyword arguments:
          None
        Returns:
          None
    """
    #pylint: disable=no-member
    total_objects = dict()
    if ARG.MANIFOLD == 'prod':
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
    else:
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')
    prefix = '/'.join([ARG.TEMPLATE, ARG.LIBRARY]) + '/'
    key_list = dict()
    separate = ['searchable_neurons']
    if 'FlyEM' not in ARG.LIBRARY:
        separate.extent(['gradient', 'zgap'])
    for obj in get_all_s3_objects(s3_client, Bucket=ARG.BUCKET, Prefix=prefix):
        which = 'default'
        for searchdir in separate:
            if searchdir in obj['Key']:
                which = searchdir
                continue
        if KEYFILE in obj['Key'] or COUNTFILE in obj['Key']:
            continue
        LOGGER.info(obj['Key'])
        if which not in key_list:
            key_list[which] = list()
            total_objects[which] = 0
        total_objects[which] += 1
        key_list[which].append(obj['Key'])
    if not total_objects['default']:
        LOGGER.error("%s/%s was not found in the %s bucket", ARG.TEMPLATE, ARG.LIBRARY, ARG.BUCKET)
        sys.exit(-1)
    # Write files
    prefix_list = ['default'] + separate
    for which in prefix_list:
        prefix = '/'.join([ARG.TEMPLATE, ARG.LIBRARY])
        if which != 'default':
            prefix += '/' + which
        object_name = '/'.join([prefix, KEYFILE])
        print("%s objects: %d" % (which, total_objects[which]))
        upload_to_aws(s3_resource, json.dumps(key_list[which], indent=4), object_name)
        object_name = '/'.join([prefix, COUNTFILE])
        upload_to_aws(s3_resource, json.dumps({"objectCount": total_objects[which]}, indent=4),
                      object_name)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Find bucket size")
    PARSER.add_argument('--bucket', dest='BUCKET', action='store',
                        default='janelia-flylight-color-depth', help='AWS S3 bucket')
    PARSER.add_argument('--template', dest='TEMPLATE', action='store',
                        default='JRC2018_Unisex_20x_HR', help='Template')
    PARSER.add_argument('--library', dest='LIBRARY', action='store',
                        default='Vienna_Gen1_LexA', help='Library')
    PARSER.add_argument('--samples', dest='SAMPLES', action='store', type=int,
                        default=0, help='Number of samples to transfer')
    PARSER.add_argument('--manifold', dest='MANIFOLD', action='store',
                        default='prod', help='S3 manifold')
    PARSER.add_argument('--test', dest='TEST', action='store_true',
                        default=False, help='Test mode (do not write to bucket)')
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
    if ARG.MANIFOLD != 'prod':
        ARG.BUCKET = '-'.join([ARG.BUCKET, ARG.MANIFOLD])
    initialize_program()
    denormalize()
