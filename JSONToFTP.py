import json
import requests
import conftest
from ftplib import FTP
from datetime import datetime
import pytz
import os
import tzlocal
import logging



def utctodate(utc_n):
    utc = pytz.utc
    utc_time = datetime.utcfromtimestamp(utc_n).replace(tzinfo=utc)
    local_timezone = tzlocal.get_localzone()
    date = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone).date()
    time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone).time()
    dt = str(date)+ "T" + str(time)
    return dt

path = 'settings.ini'
logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


logging.info("-")
logging.info("Start work")
fromNumber = conftest.get_setting(path, 'Records', 'LastNumber')

try:
    ftp = FTP()
    HOST = conftest.get_setting(path, 'FTP', 'HOST')
    LOGIN = conftest.get_setting(path, 'FTP', 'LOGIN')
    PASS = conftest.get_setting(path, 'FTP', 'PASS')
    ftp.connect(HOST)
    ftp.login(LOGIN, PASS)
except:
    logging.error("FTP: Connect error host - {}, login - , pass - ".format(HOST, LOGIN, PASS))
    logging.info("Exit")
    raise SystemExit


MaxCount = int(conftest.get_setting(path, 'General', 'limitdownload'))
NumCount = 0
hasrecords = True

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


    for record in r.json():
        #time.sleep(2)
        lastNumber = conftest.get_setting(path, 'Records', 'LastNumber')
        recordId = record["id"]

        infofile = {}
        infofile["employeeId"] = record['abonent']['phone']
        infofile["direction"] = record['direction']
        infofile["respondentNumber"] = record['phone']
        infofile["date"] = utctodate(int(str(record['date'])[:10]))
        filename = recordId + '.json'
        with open(filename, 'w', encoding='utf8') as f:
            json.dump(infofile, f, ensure_ascii=False)

        header = {'X-MPBX-API-AUTH-TOKEN': JsonToFTPToken}
        r = requests.get('https://cloudpbx.beeline.ru/apis/portal/v2/records/' + recordId + '/download', headers=header)
        with open(recordId + '.mp3', 'wb') as f:
            f.write(r.content)

        # upload to ftp
        with open(filename, 'rb') as fobj:
            ftp.storbinary('STOR ' + filename, fobj, 1024)
        logging.info("FTP: upload file {}".format(filename))
        with open(recordId + '.mp3', 'rb') as fobj:
            ftp.storbinary('STOR ' + recordId + '.mp3', fobj, 1024)
        logging.info("FTP: upload file {}".format(recordId + '.mp3'))

        # delete file from dir
        for item in os.listdir():
            if str(item).startswith(lastNumber):
                os.remove(item)



        conftest.update_setting(path, "Records", "LastNumber", recordId)
        NumCount += 1
        if NumCount >= MaxCount and MaxCount != 0:
            hasrecords = False
            break

logging.info("total upload {} files".format(NumCount))
logging.info("End work")