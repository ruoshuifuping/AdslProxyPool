import subprocess
import time

class ProxyClient():
    
    def restart_client(self):
        while True:
            (status, output) = subprocess.getstatusoutput('systemctl restart tinyproxy.service')
            if status ==0:
                print("tinyproxy 重启成功")
                time.sleep(2400)
            else:
                print("tinyproxy 重启失败，再次重启")
                
def proxy():
    client = ProxyClient()
    client.restart_client()
    
if __name__ == '__main__':
    proxy()
