import datetime
import ftplib
import os
import ssl
import time
from ssl import SSLSocket
import requests
from bs4 import BeautifulSoup as bs
import wget
import yaml

with open('bot_settings.yaml') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

host = config.get('host')
user = config.get('user')
passwd = config.get('passwd')
SSL = config.get('SSL')

dl_dir = 'downloads'
os.makedirs(dl_dir, exist_ok=True)

def check_internet():
    while 1:
        try:
            r = requests.get('http://216.58.208.238', timeout=1)
            r.raise_for_status()
            return True
        except:
            time.sleep(2)
            pass


class ReusedSslSocket(SSLSocket):
    def unwrap(self):
        pass


class MyFTP_TLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""
    
    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,
                                            server_hostname=self.host,
                                            session=self.sock.session)  # reuses TLS session
            conn.__class__ = ReusedSslSocket  # we should not close reused ssl socket when file transfers finish
        return conn, size


class FTPHandler:
    
    def __init__(self):
        try:
            if check_internet():
                self.create_con()
                self.del_con()
        except Exception as e:
            raise e
    
    def create_con(self):
        if not SSL:
            self.ftp = ftplib.FTP(host=host, user=user, passwd=passwd, timeout=30)
        else:
            ftp = MyFTP_TLS(host=host, user=user, passwd=passwd, timeout=10)
            ftp.ssl_version = ssl.PROTOCOL_SSLv23
            # ftp.login()
            ftp.prot_p()
            self.ftp = ftp
    
    def del_con(self):
        self.ftp.close()
    
    def upload_file(self, original_file):
        if original_file:
            self.create_con()
            
            cur_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = 'STOR National-Day-Calendar-Daily-News-Feed.mp3'  #  f'STOR {client_id}_{report_name}_{cur_time}.
            # csv'
            file = open(original_file, 'rb')
            self.ftp.storbinary(filename, file)
            self.del_con()
        else:
            print("Error")

# wp-content/uploads/2021/04/National-Day-Calendar-Daily-News-Feed.mp3
python_wiki_rss_url = "https://www.thenationaldailyshow.com/feed/podcast"

response = requests.get(python_wiki_rss_url)
soup = bs(response.content)

mp3_file_url = soup.select_one('enclosure').attrs['url']

filename = wget.download(mp3_file_url, out=dl_dir)


ftp_handler = FTPHandler()

ftp_handler.upload_file(filename)
print('\nFile UPloaded.\n')
