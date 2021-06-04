''' convert_neuron_tiffs.py

'''

import argparse
import json
import os
import re
import sys
import colorlog
import boto3
from botocore.exceptions import ClientError
from PIL import Image
from io import BytesIO
import requests
from tqdm import tqdm


__version__ = '0.0.1'
# Configuration
CONFIG = {'config': {'url': 'http://config.int.janelia.org/'}}
AWS = dict()
S3_SECONDS = 60 * 60 * 12


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


def initialize_s3():
    """ Initialize S3 client
        Keyword arguments:
          None
        Returns:
          S3 clientt
    """
    if ARG.MANIFOLD == 'prod':
        sts_client = boto3.client('sts')
        aro = sts_client.assume_role(RoleArn=AWS['role_arn'],
                                     RoleSessionName="AssumeRoleSession1",
                                     DurationSeconds=S3_SECONDS)
        credentials = aro['Credentials']
        s3_client = boto3.client('s3',
                                 aws_access_key_id=credentials['AccessKeyId'],
                                 aws_secret_access_key=credentials['SecretAccessKey'],
                                 aws_session_token=credentials['SessionToken'])
    else:
        s3_client = boto3.client('s3')
    return s3_client


def get_keyfile(client, bucket):
    if ARG.KEYFILE:
        with open(ARG.KEYFILE) as kfile:
            data = json.load(kfile)
        return data
    key = 'JRC2018_Unisex_20x_HR/' + ARG.LIBRARY + '/searchable_neurons/keys_denormalized.json'
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read()
    except ClientError as err:
        LOGGER.error(key)
        LOGGER.critical(err)
    except Exception as err:
        LOGGER.error(key)
        LOGGER.critical(err)
    data = json.loads(content.decode())
    return data


def convert_img(img, newname):
    ''' Convert file to PNG format
        Keyword arguments:
          img: PIL image object
          newname: new file name
        Returns:
          New filepath
    '''
    LOGGER.debug("Converting %s", newname)
    newpath = '/tmp/pngs/' + newname
    img.save(newpath, 'PNG')
    return newpath


def upload_aws(client, bucket, sourcepath, targetpath):
    """ Transfer a file to Amazon S3
        Keyword arguments:
          client: S3 client
          bucket: S3 bucket
          sourcepath: source path
          targetpath: target path
        Returns:
          url
    """
    LOGGER.debug("Uploading %s" % (targetpath))
    try:
        client.upload_file(sourcepath, bucket, targetpath,
                           ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'})
    except Exception as err:
        LOGGER.critical(err)


def convert_tiffs():
    """ Denormalize a bucket into a JSON file
        Keyword arguments:
          None
        Returns:
          None
    """
    #pylint: disable=no-member
    s3_client = initialize_s3()
    bucket = "janelia-flylight-color-depth"
    if ARG.MANIFOLD != 'prod':
        bucket += '-dev'
    data = get_keyfile(s3_client, bucket)
    order = open("png_s3cp_upload.txt", "w")
    for key in tqdm(data):
        try:
            s3_response_object = s3_client.get_object(Bucket=bucket, Key=key)
            object_content = s3_response_object['Body'].read()
            dataBytesIO = BytesIO(object_content)
            img = Image.open(dataBytesIO)
        except Exception as err:
            LOGGER.critical(err)
        if img.format != 'TIFF':
            LOGGER.error("%s is not a TIFF file", key)
        if '.tif' not in key:
            LOGGER.error("%s missing .tif extension", key)
        file = key.split('/')[-1].replace('.tif', '.png')
        tmp_path = convert_img(img, file)
        upload_path = re.sub(r'searchable_neurons.*', 'searchable_neurons/pngs/', key)
        if ARG.AWS:
            upload_aws(s3_client, bucket, tmp_path, upload_path + file)
            os.remove(tmp_path)
        else:
            order.write("%s\t%s/%s\n" % (tmp_path, bucket, upload_path + file))
    order.close()


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Produce denormalization files")
    PARSER.add_argument('--library', dest='LIBRARY', action='store',
                        default='FlyLight_Split-GAL4_Drivers', help='Library')
    PARSER.add_argument('--keyfile', dest='KEYFILE', action='store',
                        help='AWS S3 key file')
    PARSER.add_argument('--manifold', dest='MANIFOLD', action='store',
                        default='dev', help='AWS S3 manifold')
    PARSER.add_argument('--aws', dest='AWS', action='store_true',
                        default=False, help='Write PNGs to S3')
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
    convert_tiffs()
