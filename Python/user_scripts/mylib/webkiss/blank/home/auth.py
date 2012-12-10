# coding=utf8

from webkiss.web import BaseHandler

class LoginHandler(BaseHandler):
    def get(self):
        code = self.get_argument('code')
