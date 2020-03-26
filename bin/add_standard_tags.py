import sys
import boto3
from botocore.exceptions import ClientError
import requests

# Configuration
CONFIG = {'config': {'url': 'http://config.int.janelia.org/'}}
AWS = dict()
S3_CLIENT = S3_RESOURCE = ''
BUCKET = 'janelia-flylight-imagery'


def call_responder(server, endpoint):
    url = (CONFIG[server]['url'] if server else '') + endpoint
    req = requests.get(url)
    if req.status_code == 200:
        return req.json()
    sys.exit(-1)


def initialize():
    global AWS, CONFIG, S3_CLIENT, S3_RESOURCE
    data = call_responder('config', 'config/rest_services')
    CONFIG = data['config']
    data = call_responder('config', 'config/aws')
    AWS = data['config']
    sts_client = boto3.client('sts')
    aro = sts_client.assume_role(RoleArn=AWS['role_arn'],
                                 RoleSessionName="AssumeRoleSession1")
    credentials = aro['Credentials']
    S3_CLIENT = boto3.client('s3',
                             aws_access_key_id=credentials['AccessKeyId'],
                             aws_secret_access_key=credentials['SecretAccessKey'],
                             aws_session_token=credentials['SessionToken'])
    S3_RESOURCE = boto3.resource('s3',
                                 aws_access_key_id=credentials['AccessKeyId'],
                                 aws_secret_access_key=credentials['SecretAccessKey'],
                                 aws_session_token=credentials['SessionToken'])


def assign_tags():
    COUNT = SET = 0
    bucket = S3_RESOURCE.Bucket(BUCKET)
    for object in bucket.objects.filter():
        if 'Gen1' in object.key:
            tagset = [{'Key': 'DEVELOPER', 'Value': 'svirskasr'}, {'Key': 'PROJECT', 'Value': 'GEN1MCFO'}, {'Key': 'STAGE', 'Value': 'prod'}, {'Key': 'VERSION', 'Value': '1.0.0'}]
        else:
            tagset = [{'Key': 'DEVELOPER', 'Value': 'svirskasr'}, {'Key': 'PROJECT', 'Value': 'SPLITGAL4'}, {'Key': 'STAGE', 'Value': 'prod'}, {'Key': 'VERSION', 'Value': '1.0.0'}]
        response = S3_CLIENT.get_object_tagging(Bucket=BUCKET,
                                                Key=object.key)
        print(object.key)
        S3_CLIENT.put_object_tagging(Bucket=BUCKET,
                                     Key=object.key,
                                     Tagging={'TagSet': tagset})
        SET += 1
        #response = S3_CLIENT.get_object_tagging(Bucket=BUCKET,
        #                                        Key=object.key)
    print("%d are already set" % (COUNT))
    print("%d were set" % (SET))


if __name__ == '__main__':
    initialize()
    assign_tags()
