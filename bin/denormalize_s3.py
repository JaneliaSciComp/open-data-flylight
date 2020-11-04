''' denormalize_s3.py
    Denormalize an S3 bucket (with a Template/Library prefix).
    A file named keys_denormalized.json is created in the Library.
'''

import argparse
import json
import random
import sys
import tempfile
import colorlog
import boto3
from botocore.exceptions import ClientError
import requests
from simple_term_menu import TerminalMenu

__version__ = '1.1.0'
# Configuration
CONFIG = {'config': {'url': 'http://config.int.janelia.org/'}}
AWS = CDM = dict()
KEYFILE = "keys_denormalized.json"
COUNTFILE = "counts_denormalized.json"
DISTRIBUTE_FILES = ['searchable_neurons']
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
    global AWS, CDM, CONFIG # pylint: disable=W0603
    data = call_responder('config', 'config/rest_services')
    CONFIG = data['config']
    data = call_responder('config', 'config/aws')
    AWS = data['config']
    data = call_responder('config', 'config/cdm_library')
    CDM = data['config']
    random.seed()


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
        LOGGER.warning("Would have uploaded %s", object_name)
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


def write_order_file(which, body, prefix):
    """ Write an order file for use with s3cp
        Keyword arguments:
            which: first prefix (e.g. "searchable_neurons")
            body: JSON
            prefix: partial key prefix
        Returns:
            None
    """
    fname = tempfile.mktemp()
    source_file = "%s_%s.txt" % (fname, which)
    LOGGER.info("Writing temporary file %s", source_file)
    tfile = open(source_file, "w")
    tfile.write(body)
    tfile.close()
    order_file = source_file.replace('.txt', '.order')
    LOGGER.info("Writing order file %s", order_file)
    ofile = open(order_file, "w")
    for chunk in range(100):
        ofile.write("%s\t%s\n" % (source_file, '/'.join([ARG.BUCKET, prefix, 'KEYS',
                                                         str(chunk), 'keys_denormalized.json'])))
    ofile.close()


def get_parms():
    """ Query the user for the CDM library and manifold
        Keyword arguments:
            None
        Returns:
            None
    """
    if not ARG.LIBRARY:
        print("Select a library:")
        cdmlist = list()
        for cdmlib in CDM:
            if CDM[cdmlib]['name'] not in cdmlist:
                cdmlist.append(CDM[cdmlib]['name'])
        terminal_menu = TerminalMenu(cdmlist)
        chosen = terminal_menu.show()
        if chosen is None:
            LOGGER.error("No library selected")
            sys.exit(0)
        ARG.LIBRARY = cdmlist[chosen].replace(' ', '_')
    if not ARG.MANIFOLD:
        print("Select manifold to run on:")
        manifold = ['dev', 'prod']
        terminal_menu = TerminalMenu(manifold)
        chosen = terminal_menu.show()
        if chosen is None:
            LOGGER.error("No manifold selected")
            sys.exit(0)
        ARG.MANIFOLD = manifold[chosen]
    for cdmlib in CDM:
        if CDM[cdmlib]['name'].replace(' ', '_') == ARG.LIBRARY:
            print("Library %s was last modified on %s on %s"
                  % (CDM[cdmlib]['name'], CDM[cdmlib]['manifold'], CDM[cdmlib]['updated']))
            break


def denormalize():
    """ Denormalize a bucket into a JSON file
        Keyword arguments:
          None
        Returns:
          None
    """
    #pylint: disable=no-member
    get_parms()
    if ARG.MANIFOLD != 'prod':
        ARG.BUCKET = '-'.join([ARG.BUCKET, ARG.MANIFOLD])
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
    print("Processing %s on %s manifold" % (ARG.LIBRARY, ARG.MANIFOLD))
    for obj in get_all_s3_objects(s3_client, Bucket=ARG.BUCKET, Prefix=prefix):
        if KEYFILE in obj['Key'] or COUNTFILE in obj['Key']:
            continue
        which = 'default'
        LOGGER.debug(obj['Key'])
        splitkey = obj['Key'].split('/')
        if len(splitkey) >= 4:
            which = splitkey[2]
        if which not in key_list:
            key_list[which] = list()
            total_objects[which] = 0
        total_objects[which] += 1
        key_list[which].append(obj['Key'])
    if not total_objects['default']:
        LOGGER.error("%s/%s was not found in the %s bucket", ARG.TEMPLATE, ARG.LIBRARY, ARG.BUCKET)
        sys.exit(-1)
    # Write files
    prefix_template = 'https://%s.s3.amazonaws.com/%s'
    payload = {'keyname': ARG.LIBRARY, 'count': 0, 'prefix': '',
               'subprefixes': dict()}
    for which in key_list:
        prefix = '/'.join([ARG.TEMPLATE, ARG.LIBRARY])
        if which != 'default':
            prefix += '/' + which
            payload['subprefixes'][which] = {'count': total_objects[which],
                                             'prefix': prefix_template % (ARG.BUCKET, prefix)}
        else:
            payload['count'] = total_objects[which]
            payload['prefix'] = prefix_template % (ARG.BUCKET, prefix)
        object_name = '/'.join([prefix, KEYFILE])
        print("%s objects: %d" % (which, total_objects[which]))
        random.shuffle(key_list[which])
        if which in DISTRIBUTE_FILES:
            write_order_file(which, json.dumps(key_list[which], indent=4), prefix)
        else:
            upload_to_aws(s3_resource, json.dumps(key_list[which], indent=4), object_name)
        object_name = '/'.join([prefix, COUNTFILE])
        upload_to_aws(s3_resource, json.dumps({"objectCount": total_objects[which]}, indent=4),
                      object_name)
    if not ARG.TEST:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('cdm_denormalized')
        table.put_item(Item=payload)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Produce denormalization files")
    PARSER.add_argument('--bucket', dest='BUCKET', action='store',
                        default='janelia-flylight-color-depth', help='AWS S3 bucket')
    PARSER.add_argument('--template', dest='TEMPLATE', action='store',
                        default='JRC2018_Unisex_20x_HR', help='Template')
    PARSER.add_argument('--library', dest='LIBRARY', action='store',
                        default='', help='Library')
    PARSER.add_argument('--manifold', dest='MANIFOLD', action='store',
                        default='', help='S3 manifold')
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
    initialize_program()
    denormalize()
