import json

import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, Application
from adslproxy.config import *
from adslproxy.db import RedisClient


class MainHandler(RequestHandler):
    def initialize(self, redis):
        self.redis = redis

    def get(self, api=''):
        if not api:
            links = ['first', 'random', 'list', 'all', 'count']
            self.write('<h4>Welcome to ADSL Proxy API</h4>')
            for link in links:
                self.write('<a href=' + link + '>' + link + '</a><br>')

        if api == 'first':
            result = self.redis.first()
            if result:
                self.write(result)
            else:
                self.write("nothing")

        if api == 'random':
            result = self.redis.random()
            if result:
                self.write(result)
            else:
                self.write("nothing")

        if api == 'list':
            result = self.redis.list()
            if result:
                for proxy in result:
                    self.write(proxy + '<br>')
            else:
                self.write("nothing")

        if api == 'all':
            result = self.redis.all()
            if result:
                self.write(json.dumps(result))
            else:
                self.write("nothing")

        if api == 'count':
            self.write(str(self.redis.count()))
            
        if api == 'adsl1':
            result = self.redis.get('adsl1')
            if result:
                self.write(result)
            else:
                self.write("nothing")
                
        if api == 'adsl2':
            result = self.redis.get('adsl2')
            if result:
                self.write(result)
            else:
                self.write("nothing")

def server(redis, port=API_PORT, address=''):
    application = Application([
        (r'/', MainHandler, dict(redis=redis)),
        (r'/(.*)', MainHandler, dict(redis=redis)),
    ])
    application.listen(port, address=address)
    print('ADSL API Listening on', port)
    tornado.ioloop.IOLoop.instance().start()

