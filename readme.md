# ���������� �� ������  � JSONToFTP

## ��� ������ ���������
1. ������������ � API � ������� �������� ������-������
2. �������� ������ ������ ����������
3. ��� ������� ���������
    1. �������� ���������� (�������, ����������� � �.�) � ���������� �� � json-����
    2. ��������� ������ ���������
4. ��������� ���������� �� FTP-������

## �������������� ���������
1. ���������� python3 (����������� ������ 3.6)
2. ���������� pip - �������� ������� (��������� �����)
3. ���������� git
4. ����������� �����������: git clone https://github.com/jashilko/BeelineAPItoFTP.git
5. ���������� ����������� (����������) ��� ������ ������� �� ����� requirements.txt: pip install -r requirements.txt
6. ��������������� ���� �������� settings.ini
7. ��������� ������ python3 JSONToFTP.py

## ���� ��������
��������� ���: 
```
[General]
limitdownload = 100
logmode = INFO
sleep = 1

[Records]
lastnumber = 1

[BeelineAPI]
jsontoftptoken = *****

[FTP]
host = ftp.localhost.ru
login = xxx
pass = yyy
```
* limitdownload = [������������� �����] - ������������ ���������� ��� ������ (json + mp3), ������� ������� ���������� �� ���� �������
* logmode = [**INFO**, DEBUG, ERROR] - ����� ������������ 
* sleep = [������������� �����] - �������� � �������� ����� ���������� ������ �� FTP
* lastnumber = [������������� �����] - �� ��������� ������������ ������. ��� ������ ������ ������� ���������� = 1
* jsontoftptoken = [GUID] - ����, �������� ������ ��������� �������
* host, login, pass - ����, ����� � ������ ��� ������� � SFTP

## ���������� �������
���� ������ ��������� �������������, �� ��� ����� �������� ��������� �������:
1. ��������� ��������� ��������� git pull
2. �������� ����������� pip install -r requirements.txt