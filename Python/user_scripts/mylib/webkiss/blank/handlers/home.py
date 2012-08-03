# coding=utf8

from webkiss.web import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        self.render('base.html')
