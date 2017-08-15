import re
import time
import requests as rq
from requests.exceptions import ConnectionError, ReadTimeout
from adslproxy.db import RedisClient
from adslproxy.config import *
import platform

if platform.python_version().startswith('2.'):
    import commands as subprocess
elif platform.python_version().startswith('3.'):
    import subprocess
else:
    raise ValueError('python version must be 2 or 3')


class Sender():
    def __init__(self):
        self.proxy = None
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36'}
        
    def get_ip(self, ifname=ADSL_IFNAME):
        (status, output) = subprocess.getstatusoutput('ifconfig')
        if status == 0:
            pattern = re.compile(ifname + '.*?inet.*?(\d+\.\d+\.\d+\.\d+).*?netmask', re.S)
            result = re.search(pattern, output)
            if result:
                ip = result.group(1)                    
                return ip                    

    def test_proxy(self, proxy):
        try:
            if proxy != self.proxy:
                html = rq.get('https://www.baidu.com/',proxies=proxy,timeout = 10)
                if html.status_code == 200:
                    self.proxy = proxy
                    return True
                else:
                    self.proxy = proxy
                    return False
            else:
                self.proxy = proxy
                return False
        except:
            return False

    def remove_proxy(self):
        self.redis = RedisClient()
        self.redis.remove(CLIENT_NAME)
        print('Successfully Removed Proxy')

    def set_proxy(self, proxy):
        self.redis = RedisClient()
        if self.redis.set(CLIENT_NAME, proxy):
            print('Successfully Set Proxy', proxy)

    def adsl(self):
        while True:
            print('ADSL Start, Please wait')           
            (status, output) = subprocess.getstatusoutput(ADSL_BASH)
            if status == 0:
                print('ADSL Successfully')
                ip = self.get_ip()
                if ip:
                    proxy = {'http':'http://' + '{ip}:{port}'.format(ip=ip, port=PROXY_PORT)}
                    print("new proxy ",proxy)
                    if self.test_proxy(proxy):
                        print('Valid Proxy')
                        self.set_proxy(proxy)
                        print('Sleeping',ADSL_CYCLE + 15)
                        time.sleep(ADSL_CYCLE)
                        self.remove_proxy()
                        time.sleep(15)
                    else:
                        print('Invalid Proxy')
                else:
                    print('Get IP Failed, Re Dialing')
                    time.sleep(ADSL_ERROR_CYCLE)
            else:
                print('ADSL Failed, Please Check')
                time.sleep(ADSL_ERROR_CYCLE)


def run():
    sender = Sender()
    sender.adsl()


if __name__ == '__main__':
    run()
