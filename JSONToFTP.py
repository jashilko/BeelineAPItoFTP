import json
import requests
import conftest
from datetime import datetime
import pytz
import os
import tzlocal
import logging
import pysftp
import paramiko
import time

class My_Connection(pysftp.Connection):
    def __init__(self, *args, **kwargs):
        self._sftp_live = False
        self._transport = None
        super().__init__(*args, **kwargs)

def utctodate(utc_n):
    utc = pytz.utc
    utc_time = datetime.utcfromtimestamp(utc_n).replace(tzinfo=utc)
    local_timezone = tzlocal.get_localzone()
    date = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone).date()
    time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone).time()
    dt = str(date)+ "T" + str(time)
    return dt
dir = os.path.dirname(__file__) + '/'
print("Current dir - " + dir)
path = dir + 'settings.ini'
date_log = datetime.now().strftime("%Y-%m-%d")
logmode = conftest.get_setting(path, 'General', 'logmode')
if logmode == 'INFO':
    logging.basicConfig(filename = dir + "log/" + date_log + "-log.txt", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
elif logmode == 'DEBUG':
    logging.basicConfig(filename=dir + "log/" + date_log + "-log.txt", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename=dir + "log/" + date_log + "-log.txt", level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("-")
logging.info("Start work")
fromNumber = conftest.get_setting(path, 'Records', 'LastNumber')
sleep = 0
sleep = int(conftest.get_setting(path, 'General', 'sleep'))


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

try:
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    HOST = conftest.get_setting(path, 'FTP', 'HOST')
    LOGIN = conftest.get_setting(path, 'FTP', 'LOGIN')
    PASS = conftest.get_setting(path, 'FTP', 'PASS')
    sftp = My_Connection(HOST, username=LOGIN, password=PASS, cnopts=cnopts)
except:
    logging.error("FTP: Connect error host - {}, login - , pass - ".format(HOST, LOGIN, PASS))
    logging.info("Exit")
    raise SystemExit


MaxCount = int(conftest.get_setting(path, 'General', 'limitdownload'))
NumCount = 0
hasrecords = True
firstFile = ""
lastfile = ""

while hasrecords:
    JsonToFTPToken = conftest.get_setting(path, 'BeelineAPI', 'JsonToFTPToken')
    header = {'X-MPBX-API-AUTH-TOKEN': JsonToFTPToken}
    param = {'id': fromNumber}
    r = requests.get('https://cloudpbx.beeline.ru/apis/portal/records', headers=header, params=param)
    response = r.json()
    if r.status_code != 200:
        logging.error("Beeline: Response answer - {}".format(r.status_code))
        logging.info("Exit")
        raise SystemExit
    if len(r.json()) == 0:
        logging.info("Beeline: No records")
        logging.info("Exit")
        raise SystemExit


    for record in r.json():
        lastNumber = conftest.get_setting(path, 'Records', 'LastNumber')
        recordId = record["id"]

        infofile = {}
        infofile["employeeId"] = record['abonent']['phone']
        direction = ""
        if record['direction'] == "OUTBOUND":
            direction = "out"
        elif record['direction'] == "INBOUND":
            direction = "in"
        infofile["direction"] = direction
        infofile["language"] = "ru"
        infofile["respondentNumber"] = record['phone']
        infofile["dateTime"] = utctodate(int(str(record['date'])[:10]))
        filename = recordId + '.json'
        with open(dir + filename, 'w', encoding='utf8') as f:
            json.dump(infofile, f, ensure_ascii=False)
        if firstFile == "":
            firstFile = recordId

        header = {'X-MPBX-API-AUTH-TOKEN': JsonToFTPToken}
        r = requests.get('https://cloudpbx.beeline.ru/apis/portal/v2/records/' + recordId + '/download', headers=header)
        with open(dir + recordId + '.mp3', 'wb') as f:
            f.write(r.content)

        # upload to ftp
        try:
            sftp.put(dir + filename)
            logging.debug("FTP: upload file {}".format(filename))
            sftp.put(dir + recordId + '.mp3')
            logging.debug("FTP: upload file {}".format(recordId + '.mp3'))
        except paramiko.ssh_exception.SSHException as e:
            print('SSH error, you need to add the public key of your remote in your local known_hosts file first.', e)
            logging.error("FTP: SSH error, you need to add the public key of your remote in your "
                          "local known_hosts file first. - {}".format(e))
            logging.info("SystemExit")
            raise SystemExit
        except Exception as e:
            logging.error("FTP: Upload error - {}".format(e))
            logging.info("SystemExit")
            raise SystemExit

        # delete file from dir
        for item in os.listdir(dir):
            if str(item).startswith(lastNumber):
                os.remove(dir + item)

        time.sleep(sleep)


        conftest.update_setting(path, "Records", "LastNumber", recordId)
        NumCount += 1
        if NumCount >= MaxCount and MaxCount != 0:
            hasrecords = False
            break

lastfile = recordId
logging.info("total upload {} files. First - {}, last - {}".format(NumCount, firstFile, lastfile))
logging.info("End work")