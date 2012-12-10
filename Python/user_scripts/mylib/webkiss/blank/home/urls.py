# coding=utf8

from .home import HomeHandler
from .auth import LoginHandler

urls = [
    (r'', HomeHandler),
    (r'login$', LoginHandler),
]
