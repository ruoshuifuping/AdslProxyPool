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
                proxies = {'http':'http://'+proxy}
                headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
                html = rq.get(TEST_URL,proxies=proxies,headers=headers,timeout = 20)
                if html.status_code == 200:
                    if self.get_yanzhengma(html.text):
                        self.proxy.append(proxy)
                        if len(self.proxy) > 25:
                            self.proxy.remove(self.proxy[0])
                        return True
                    else:
                        self.proxy.append(proxy)
                        if len(self.proxy) > 25:
                            self.proxy.remove(self.proxy[0])
                        return False
                else:
                    self.proxy.append(proxy)
                    if len(self.proxy) > 25:
                        self.proxy.remove(self.proxy[0])
                    return False
            else:
                self.proxy.append(proxy)
                if len(self.proxy) > 25:
                    self.proxy.remove(self.proxy[0])
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
    
    def get_yanzhengma(self,html):
        n = re.findall('Robot Check',html)
        if not n:
            return True
        else:
            return False

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
                        self.set_proxy(proxy)
                        print('Sleeping',ADSL_CYCLE + 5)
                        time.sleep(ADSL_CYCLE)
                        self.remove_proxy()
                        time.sleep(5)
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
