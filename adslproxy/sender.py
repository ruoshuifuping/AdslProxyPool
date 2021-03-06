import re
import time
import requests as rq
from requests.exceptions import ConnectionError, ReadTimeout
from adslproxy.db import RedisClient
from adslproxy.config import *
import platform
from random import choice

if platform.python_version().startswith('2.'):
    import commands as subprocess
elif platform.python_version().startswith('3.'):
    import subprocess
else:
    raise ValueError('python version must be 2 or 3')


class Sender():
    def __init__(self):
        self.proxy = []
        self.proxies = None
        self.headers = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        ]
        
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
            if proxy not in self.proxy:
                print('start texting')
                m = choice(self.headers)
                headers = {'User-Agent':m}
                html = rq.get(TEST_URL ,headers=headers,timeout = 5)
                if html.status_code == 200:
                    self.proxy.append(proxy)
                    self.proxies = proxy + "\t" + m
                    if len(self.proxy) > 50:
                        self.proxy.remove(self.proxy[0])
                    #if '66.0.3359' in m:
                        #subprocess.getstatusoutput('systemctl restart  tinyproxy.service')
                    return True
                else:
                    self.proxy.append(proxy)
                    print("连接状态不是200")
                    if len(self.proxy) > 50:
                        self.proxy.remove(self.proxy[0])
                    return False
            else:
                print("和之前IP重复")
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
                    proxy = '{ip}:{port}'.format(ip=ip, port=PROXY_PORT)
                    print("new proxy ",proxy)
                    if self.test_proxy(proxy):
                        print('Valid Proxy')
                        self.set_proxy(self.proxies)
                        print('Sleeping',ADSL_CYCLE)
                        time.sleep(ADSL_CYCLE)
                        self.remove_proxy()
                    else:
                        print('Invalid Proxy')
                        time.sleep(5)
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
