''' This program will Upload Color Depth MIPs to AWS S3.
'''
__version__ = '1.0.0'

import argparse
import os
import socket
import sys
from time import strftime, time
import boto3
from botocore.exceptions import ClientError
import colorlog
import jwt
import requests
import MySQLdb
from PIL import Image


# Configuration
CONFIG = {'config': {'url': 'http://config.int.janelia.org/'}}
AWS = dict()
LIBRARY = dict()
DATABASE = 'sage'
CONN = dict()
CURSOR = dict()

GEN1_COLLECTION = ['flylight_gen1_gal4', 'flylight_gen1_lexa', 'flylight_vt_gal4_screen',
                   'flylight_vt_lexa_screen', 'flylight_gen1_mcfo_case_1']
CONVERSION_REQUIRED = ['flyem_hemibrain']
VERSION_REQUIRED = ['flyem_hemibrain']
CDM_ALIGNMENT_SPACE = 'JRC2018_Unisex_20x_HR'
COUNT = {'Amazon S3 uploads': 0, 'Files to upload': 0, 'Samples': 0, 'No Consensus': 0,
         'No sampleRef': 0, 'No publishing name': 0, 'No driver': 0, 'No release': 0,
         'Skipped': 0, 'Already on S3': 0, 'Already on JACS': 0, 'Bad driver': 0}
PNAME = dict()
REC = {'line': '', 'slide_code': '', 'gender': '', 'objective': '', 'area': ''}
S3_CLIENT = S3_RESOURCE = ''
MAX_SIZE = 500
CREATE_THUMBNAIL = False
S3_SECONDS = 60 * 60 * 12


def call_responder(server, endpoint, payload='', authenticate=False):
    ''' Call a responder
        Keyword arguments:
          server: server
          endpoint: REST endpoint
          payload: payload for POST requests
          authenticate: pass along token in header
        Returns:
          JSON response
    '''
    url = (CONFIG[server]['url'] if server else '') + endpoint
    try:
        if payload or authenticate:
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer " + os.environ['JACS_JWT']}
        if payload:
            headers['Accept'] = 'application/json'
            headers['host'] = socket.gethostname()
            req = requests.put(url, headers=headers, json=payload)
        else:
            if authenticate:
                req = requests.get(url, headers=headers)
            else:
                req = requests.get(url)
    except requests.exceptions.RequestException as err:
        LOGGER.critical(err)
        sys.exit(-1)
    if req.status_code == 200:
        return req.json()
    print("Could not get response from %s: %s" % (url, req.text))
    sys.exit(-1)


def sql_error(err):
    """ Log a critical SQL error and exit """
    try:
        LOGGER.critical('MySQL error [%d]: %s', err.args[0], err.args[1])
    except IndexError:
        LOGGER.critical('MySQL error: %s', err)
    sys.exit(-1)


def db_connect(dbd):
    """ Connect to a database
        Keyword arguments:
          dbd: database dictionary
    """
    LOGGER.info("Connecting to %s on %s", dbd['name'], dbd['host'])
    try:
        conn = MySQLdb.connect(host=dbd['host'], user=dbd['user'],
                               passwd=dbd['password'], db=dbd['name'])
    except MySQLdb.Error as err:
        sql_error(err)
    try:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        return conn, cursor
    except MySQLdb.Error as err:
        sql_error(err)


def decode_token(token):
    ''' Decode a given JWT token
        Keyword arguments:
          token: JWT token
        Returns:
          decoded token JSON
    '''
    try:
        response = jwt.decode(token, verify=False)
    except jwt.exceptions.DecodeError:
        LOGGER.critical("Token failed validation")
        sys.exit(-1)
    except jwt.exceptions.InvalidTokenError:
        LOGGER.critical("Could not decode token")
        sys.exit(-1)
    return response


def initialize_s3():
    """ Initialize
    """
    global S3_CLIENT, S3_RESOURCE # pylint: disable=W0603
    LOGGER.info("Opening S3 client and resource")
    if ARG.MANIFOLD == 'dev':
        S3_CLIENT = boto3.client('s3')
        S3_RESOURCE = boto3.resource('s3')
    else:
        sts_client = boto3.client('sts')
        aro = sts_client.assume_role(RoleArn=AWS['role_arn'],
                                     RoleSessionName="AssumeRoleSession1",
                                     DurationSeconds=S3_SECONDS)
        credentials = aro['Credentials']
        S3_CLIENT = boto3.client('s3',
                                 aws_access_key_id=credentials['AccessKeyId'],
                                 aws_secret_access_key=credentials['SecretAccessKey'],
                                 aws_session_token=credentials['SessionToken'])
        S3_RESOURCE = boto3.resource('s3',
                                     aws_access_key_id=credentials['AccessKeyId'],
                                     aws_secret_access_key=credentials['SecretAccessKey'],
                                     aws_session_token=credentials['SessionToken'])


def initialize_program():
    """ Initialize
    """
    global AWS, CONFIG, LIBRARY # pylint: disable=W0603
    data = call_responder('config', 'config/rest_services')
    CONFIG = data['config']
    data = call_responder('config', 'config/aws')
    AWS = data['config']
    data = call_responder('config', 'config/db_config')
    manifold = 'prod'
    if ARG.LIBRARY == 'flylight_splitgal4_drivers':
        manifold = 'staging'
    (CONN[DATABASE], CURSOR[DATABASE]) = db_connect(data['config'][DATABASE][manifold])
    if DATABASE != 'sage':
        (CONN['sage'], CURSOR['sage']) = db_connect(data['config']['sage']['prod'])
    data = call_responder('config', 'config/cdm_libraries')
    LIBRARY = data['config']
    if ARG.LIBRARY not in LIBRARY:
        LOGGER.critical("Unknown library %s", ARG.LIBRARY)
        sys.exit(-1)
    if 'JACS_JWT' not in os.environ:
        LOGGER.critical("Missing token - set in JACS_JWT environment variable")
        sys.exit(-1)
    response = decode_token(os.environ['JACS_JWT'])
    if int(time()) >= response['exp']:
        LOGGER.critical("Your token is expired")
        sys.exit(-1)
    LOGGER.info("Authenticated as %s", response['full_name'])
    initialize_s3()


def upload_aws(bucket, dirpath, fname, newname):
    ''' Transfer a file to Amazon S3
        Keyword arguments:
          bucket: S3 bucket
          dirpath: source directory
          fname: file name
          newname: new file name
        Returns:
          url
    '''
    COUNT['Files to upload'] += 1
    complete_fpath = '/'.join([dirpath, fname])
    if ARG.MANIFOLD != 'prod':
        bucket += '-' + ARG.MANIFOLD
    library = LIBRARY[ARG.LIBRARY].replace(' ', '_')
    if ARG.LIBRARY in VERSION_REQUIRED:
        library += '_v' + ARG.VERSION
    object_name = '/'.join([REC['alignment_space'], library, newname])
    LOGGER.debug("Uploading %s to S3 as %s", complete_fpath, object_name)
    url = '/'.join([AWS['base_aws_url'], bucket, object_name])
    url = url.replace(' ', '+')
    if not ARG.WRITE:
        LOGGER.info(newname)
        COUNT['Amazon S3 uploads'] += 1
        return url
    mimetype = 'image/png' if '.png' in newname else 'image/jpeg'
    tags = 'PROJECT=CDCS&STAGE=' + ARG.MANIFOLD + '&DEVELOPER=svirskasr&' \
           + 'VERSION=' + __version__
    try:
        S3_CLIENT.upload_file(complete_fpath, bucket,
                              object_name,
                              ExtraArgs={'ContentType': mimetype, 'ACL': 'public-read',
                                         'Tagging': tags})
        #obj = S3_RESOURCE.Object(bucket, object_name)
        #obj.copy_from(CopySource={'Bucket': bucket,
        #                          'Key': object_name},
        #              MetadataDirective="REPLACE",
        #              ContentType=mimetype)
        #object_acl = S3_RESOURCE.ObjectAcl(bucket, object_name)
        #object_acl.put(ACL='public-read')
    except ClientError as err:
        LOGGER.critical(err)
        return False
    COUNT['Amazon S3 uploads'] += 1
    return url


def degenerate_line(line0):
    ''' Return the degenerate line name
        Keyword arguments:
          line: full line name
        Returns:
          Degenerate line name
    '''
    comp = line0.split('_')
    return '_'.join(comp[0:2])


def get_r_line(line0):
    ''' Return the Gen1 line name
        Keyword arguments:
          line0: line name
        Returns:
          Gen1 line name
    '''
    r_line = 'R' + line0.split('_')[1]
    return r_line


def publishing_name_mapping():
    ''' Create a mapping of lines to publishing names
        Keyword arguments:
          None
        Returns:
          mapping dictionary
    '''
    mapping = dict()
    if '_vt_' in ARG.LIBRARY or ARG.LIBRARY == 'flylight_gen1_mcfo_case_1':
        data = call_responder('config', 'config/vt_conversion')
        vtm = data['config']
        for vtid in vtm:
            mapping['BJD_' + vtm[vtid]] = vtid
    else:
        if ARG.LIBRARY == 'flylight_splitgal4_drivers':
            stmt = "SELECT DISTINCT published_to,original_line,line FROM image_data_mv"
            lkey = 'original_line'
            mapcol = 'line'
        else:
            stmt = "SELECT DISTINCT published_to,line,publishing_name FROM image_data_mv " \
                   + "WHERE published_to IS NOT NULL"
            lkey = 'line'
            mapcol = 'publishing_name'
        try:
            CURSOR[DATABASE].execute(stmt)
            rows = CURSOR[DATABASE].fetchall()
        except MySQLdb.Error as err:
            sql_error(err)
        for row in rows:
            if not row[lkey]:
                #row[lkey] = row[mapcol]
                print(row)
                LOGGER.error("Missing original line for %s", row[mapcol])
                sys.exit(-1)
            if 'FLEW' in row['published_to']:
                row[lkey] = degenerate_line(row[lkey])
                if not row[mapcol]:
                    row[mapcol] = get_r_line(row[lkey])
                row[mapcol] = row[mapcol].replace('L', '')
            mapping[row[lkey]] = row[mapcol]
            if not row[mapcol]:
                LOGGER.error("Missing publishing name for %s", row[lkey])
    return mapping


def get_line_mapping():
    ''' Create a mapping of lines to publishing names, drivers, and releases
        Keyword arguments:
          None
        Returns:
          mapping dictionary
          driver dictionary
          release dictionary
    '''
    driver = dict()
    release = dict()
    LOGGER.info("Getting line/publishing name mapping")
    mapping = publishing_name_mapping()

    # Populate driver dict
    LOGGER.info("Getting line/driver mapping")
    try:
        CURSOR['sage'].execute("SELECT name,value FROM line_property_vw WHERE " \
                               + "type='flycore_project'")
        rows = CURSOR['sage'].fetchall()
    except MySQLdb.Error as err:
        sql_error(err)
    for row in rows:
        driver[row['name']] = row['value'].replace("_Collection", "").replace("-", "_")
    # Populate release dict
    if ARG.LIBRARY == 'flylight_splitgal4_drivers':
        LOGGER.info("Getting line/release mapping")
        try:
            CURSOR['sage'].execute("SELECT line,GROUP_CONCAT(DISTINCT alps_release) AS alps " \
                                   + "FROM image_data_mv WHERE alps_release IS NOT NULL GROUP BY 1")
            rows = CURSOR['sage'].fetchall()
        except MySQLdb.Error as err:
            sql_error(err)
        for row in rows:
            release[row['line']] = row['alps']
    return mapping, driver, release


def get_publishing_name(sdata, mapping):
    ''' Return a publishing name for this sample
        Keyword arguments:
          sdata: sample record
          mapping: publishing name mapping dictionary
        Returns:
          publishing name
    '''
    if len(sdata) > 1:
        LOGGER.critical("More than one sample found")
        sys.exit(-1)
    if sdata[0]['line'] not in sdata[0]['name']:
        LOGGER.critical("Line %s not present in name %s", sdata[0]['line'], sdata[0]['name'])
        sys.exit(-1)
    publishing_name = ''
    if 'publishingName' in sdata[0] and sdata[0]['publishingName']:
        if ARG.LIBRARY in GEN1_COLLECTION and sdata[0]['publishingName'].endswith('L'):
            sdata[0]['publishingName'] = sdata[0]['publishingName'].replace('L', '')
        publishing_name = sdata[0]['publishingName']
    elif sdata[0]['line'] in mapping:
        publishing_name = mapping[sdata[0]['line']]
    elif ARG.LIBRARY in GEN1_COLLECTION:
        lookup = degenerate_line(sdata[0]['line'])
        if mapping.get(lookup):
            publishing_name = mapping[lookup]
        else:
            publishing_name = get_r_line(sdata[0]['line'])
    elif 'JRC_SS' in sdata[0]['line']:
        short = sdata[0]['line'].replace('JRC_SS', 'SS')
        if short in mapping:
            publishing_name = short
    LOGGER.debug("%s -> %s", sdata[0]['line'], publishing_name)
    return publishing_name


def convert_file(sourcepath, newname):
    ''' Convert file to PNG format
        Keyword arguments:
          sourcepath: source filepath
          newname: new file name
        Returns:
          New filepath
    '''
    newpath = '/tmp/' + newname
    with Image.open(sourcepath) as image:
        image.save(newpath, 'PNG')
    return newpath


def process_hemibrain(smp):
    ''' Return the file name for a hemibrain sample.
        Keyword arguments:
          smp: sample record
        Returns:
          New file name
    '''
    bodyid, status = smp['name'].split('_')[0:2]
    newname = '%s-%s-%s-CDM.png' \
    % (bodyid, status, REC['alignment_space'])
    smp['filepath'] = convert_file(smp['filepath'], newname)
    return newname


def process_flylight_splitgal4_drivers(sdata, sid, release):
    ''' Return the file name for a light microscopy sample.
        Keyword arguments:
          sdata: sample record
          sid: sample ID
          release: release mapping dictionary
        Returns:
          True/False for success
    '''
    if ARG.LIBRARY == 'flylight_splitgal4_drivers' and ARG.RELEASE:
        if sdata[0]['line'] not in release:
            COUNT['No release'] += 1
            err_text = "No release for sample %s (%s)" % (sid, sdata[0]['line'])
            LOGGER.error(err_text)
            ERR.write(err_text + "\n")
            return False
        if ARG.RELEASE not in release[sdata[0]['line']]:
            COUNT['Skipped'] += 1
            return False
    return True


def translate_slide_code(isc, line0):
    ''' Translate a slide code to remove initials.
        Keyword arguments:
          isc: initial slide doce
          line0: line
        Returns:
          New slide code
    '''
    if 'sample_BJD' in isc:
        return isc.replace("BJD", "")
    if 'GMR' in isc:
        new = isc.replace(line0 + "_", "")
        new = new.replace("-", "_")
        return new
    return isc


def process_light(smp, mapping, driver, release):
    ''' Return the file name for a light microscopy sample.
        Keyword arguments:
          smp: sample record
          mapping: publishing name mapping dictionary
          driver: driver mapping dictionary
          release: release mapping dictionary
        Returns:
          New file name
    '''
    if 'sampleRef' not in smp:
        COUNT['No sampleRef'] += 1
        err_text = "No sampleRef for %s (%s)" % (smp['_id'], smp['name'])
        LOGGER.warning(err_text)
        ERR.write(err_text + "\n")
        return False
    sid = (smp['sampleRef'].split('#'))[-1]
    LOGGER.info(sid)
    sdata = call_responder('jacs', 'data/sample?sampleId=' + sid)
    if not process_flylight_splitgal4_drivers(sdata, sid, release):
        return False
    publishing_name = get_publishing_name(sdata, mapping)
    if sdata[0]['line'] == 'No Consensus':
        COUNT['No Consensus'] += 1
        err_text = "No consensus line for sample %s (%s)" % (sid, sdata[0]['line'])
        LOGGER.error(err_text)
        ERR.write(err_text + "\n")
        if ARG.WRITE:
            return False
    if publishing_name == 'No Consensus':
        COUNT['No Consensus'] += 1
        err_text = "No consensus line for sample %s (%s)" % (sid, sdata[0]['line'])
        LOGGER.error(err_text)
        ERR.write(err_text + "\n")
        if ARG.WRITE:
            return False
    if not publishing_name:
        COUNT['No publishing name'] += 1
        err_text = "No publishing name for sample %s (%s)" % (sid, sdata[0]['line'])
        LOGGER.error(err_text)
        ERR.write(err_text + "\n")
        #if ARG.WRITE: PLUG
        #    sys.exit(-1)
        return False
    if publishing_name not in PNAME:
        PNAME[publishing_name] = 1
    else:
        PNAME[publishing_name] += 1
    REC['line'] = publishing_name
    #REC['slide_code'] = translate_slide_code(sdata[0]['slideCode'], sdata[0]['line'])
    REC['slide_code'] = sdata[0]['slideCode']
    REC['gender'] = sdata[0]['gender']
    REC['objective'] = smp['objective']
    REC['area'] = smp['anatomicalArea'].lower()
    if ('_L' in sdata[0]['line'] and ARG.LIBRARY == 'flylight_gen1_gal4') \
       or ('_L' not in sdata[0]['line'] and ARG.LIBRARY == 'flylight_gen1_lexa'):
        COUNT['Bad driver'] += 1
        err_text = "Bad driver for sample %s (%s)" % (sid, sdata[0]['line'])
        LOGGER.error(err_text)
        ERR.write(err_text + "\n")
        if ARG.WRITE:
            sys.exit(-1)
        return False
    if sdata[0]['line'] in driver:
        drv = driver[sdata[0]['line']]
    else:
        COUNT['No driver'] += 1
        err_text = "No driver for sample %s (%s)" % (sid, sdata[0]['line'])
        LOGGER.error(err_text)
        ERR.write(err_text + "\n")
        if ARG.WRITE:
            sys.exit(-1)
        return False
    fname = os.path.basename(smp['filepath'])
    chan = fname.split('-')[-1]
    chan = chan.split('_')[0].replace('CH', '')
    if chan not in ['1', '2', '3', '4']:
        LOGGER.critical("Could not find channel for %s", fname)
        sys.exit(-1)
    newname = '%s-%s-%s-%s-%s-%s-%s-CDM_%s.png' \
        % (REC['line'], REC['slide_code'], drv, REC['gender'],
           REC['objective'], REC['area'], REC['alignment_space'], chan)
    return newname


def calculate_size(dim):
    ''' Return the fnew dimensions for an image. The longest side will be scaled down to MAX_SIZE.
        Keyword arguments:
          dim: tuple with (X,Y) dimensions
        Returns:
          Tuple with new (X,Y) dimensions
    '''
    xdim, ydim = list(dim)
    if xdim <= MAX_SIZE and ydim <= MAX_SIZE:
        return dim
    if xdim > ydim:
        ratio = xdim / MAX_SIZE
        xdim, ydim = [MAX_SIZE, int(ydim/ratio)]
    else:
        ratio = ydim / MAX_SIZE
        xdim, ydim = [int(xdim/ratio), MAX_SIZE]
    return tuple((xdim, ydim))


def resize_image(image_path, resized_path):
    ''' Read in an image, resize it, and write a copy.
        Keyword arguments:
          image_path: CDM image path
          resized_path: path for resized image
        Returns:
          None
    '''
    with Image.open(image_path) as image:
        new_size = calculate_size(image.size)
        image.thumbnail(new_size)
        image.save(resized_path, 'JPEG')


def produce_thumbnail(dirpath, fname, newname, url):
    ''' Transfer a file to Amazon S3
        Keyword arguments:
          dirpath: source directory
          fname: file name
        Returns:
          thumbnail url
    '''
    turl = url.replace('.png', '.jpg')
    turl = turl.replace(AWS['s3_bucket']['cdm'], AWS['s3_bucket']['cdm-thumbnail'])
    if CREATE_THUMBNAIL:
        tname = newname.replace('.png', '.jpg')
        complete_fpath = '/'.join([dirpath, fname])
        resize_image(complete_fpath, '/tmp/' + tname)
        turl = upload_aws(AWS['s3_bucket']['cdm-thumbnail'], '/tmp', tname, tname)
    return turl


def upload_cdms():
    ''' Upload color depth MIPs to AWS S3
        Keyword arguments:
          None
        Returns:
          None
    '''
    mapping, driver, release = get_line_mapping()
    samples = call_responder('jacsv2', 'colorDepthMIPs?libraryName=' + ARG.LIBRARY \
                             + '&alignmentSpace=' + CDM_ALIGNMENT_SPACE, '', True)
    print("Samples for %s: %d" % (ARG.LIBRARY, len(samples)))
    for smp in samples:
        if ARG.SAMPLES and COUNT['Samples'] >= ARG.SAMPLES:
            break
        COUNT['Samples'] += 1
        if 'publicImageUrl' in smp and smp['publicImageUrl'] and not ARG.REWRITE:
            COUNT['Already on JACS'] += 1
            continue
        if ARG.CHECK:
            thumb = smp['publicThumbnailUrl']
            request = requests.get(thumb)
            if request.status_code == 200: 
                COUNT['Already on S3'] += 1
                #LOGGER.warning("%s is already on AWS S3", smp['publicThumbnailUrl'])
                continue
        REC['alignment_space'] = smp['alignmentSpace']
        if ARG.LIBRARY == 'flyem_hemibrain':
            newname = process_hemibrain(smp)
            if not newname:
                continue
        else:
            newname = process_light(smp, mapping, driver, release)
            if not newname:
                continue
        dirpath = os.path.dirname(smp['filepath'])
        fname = os.path.basename(smp['filepath'])
        url = upload_aws(AWS['s3_bucket']['cdm'], dirpath, fname, newname)
        if url:
            turl = produce_thumbnail(dirpath, fname, newname, url)
            if ARG.WRITE:
                if ARG.LIBRARY in CONVERSION_REQUIRED:
                    os.remove(smp['filepath'])
                pay = {"class": "org.janelia.model.domain.gui.cdmip.ColorDepthImage",
                       "publicImageUrl": url,
                       "publicThumbnailUrl": turl}
                call_responder('jacsv2', 'colorDepthMIPs/' + smp['_id'] \
                               + '/publicURLs', pay, True)
            else:
                LOGGER.info(url)
        else:
            LOGGER.error("Could not transfer %s", fname)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description="Upload Color Depth MIPs to AWS S3")
    PARSER.add_argument('--library', dest='LIBRARY', action='store',
                        default='flylight_splitgal4_drivers', help='color depth library')
    PARSER.add_argument('--release', dest='RELEASE', action='store',
                        help='ALPS release')
    PARSER.add_argument('--rewrite', dest='REWRITE', action='store_true',
                        default=False,
                        help='Flag, Update image in AWS and on JACS')
    PARSER.add_argument('--check', dest='CHECK', action='store_true',
                        default=False,
                        help='Flag, Check for previous AWS upload')
    PARSER.add_argument('--manifold', dest='MANIFOLD', action='store',
                        default='prod', help='S3 manifold')
    PARSER.add_argument('--write', dest='WRITE', action='store_true',
                        default=False,
                        help='Flag, Actually write to AWS/JACS')
    PARSER.add_argument('--samples', dest='SAMPLES', action='store', type=int,
                        default=0, help='Number of samples to transfer')
    PARSER.add_argument('--version', dest='VERSION', action='store',
                        default='1.0', help='EM Version')
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

    ERR_FILE = 'upload_cdms_errors_%s.txt' % (strftime("%Y%m%dT%H%M%S"))
    LINE_FILE = 'upload_cdms_lines_%s.txt' % (strftime("%Y%m%dT%H%M%S"))
    ERR = open(ERR_FILE, 'w')
    LINE = open(LINE_FILE, 'w')

    if ARG.LIBRARY == 'flylight_splitgal4_drivers':
        DATABASE = 'mbew'
    initialize_program()
    upload_cdms()
    ERR.close()
    for line in sorted(PNAME):
        LINE.write("%s\t%d\n" % (line, PNAME[line]))
    for key in sorted(COUNT):
        print("%-20s %d" % (key + ':', COUNT[key]))
    LINE.close()
    for fpath in [ERR_FILE, LINE_FILE]:
        if not os.path.getsize(fpath):
            os.remove(fpath)
    sys.exit(0)
