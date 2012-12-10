# coding=utf8
""" 入口模块, 初始化设定. """

import os, sys
# 将当前目录加入 sys.path
#sys.path.insert(0, os.path.abspath('.'))

if 'SERVER_SOFTWARE' in os.environ:
    # 在部署环境加入libs目录到sys.path
    sys.path.insert(0, os.path.abspath('libs'))

from settings import urls, settings
from webkiss.utils import is_sae
import webkiss.db as db
from webkiss.web import Patterns

urls = Patterns(urls)

if is_sae:
    import sae.const

    database_dialect = 'mysql://%s:%s@%s:%s/%s' % (sae.const.MYSQL_USER, sae.const.MYSQL_PASS, sae.const.MYSQL_HOST, sae.const.MYSQL_PORT, sae.const.MYSQL_DB)
    settings['database_dialect'] = database_dialect
    settings['redirect_uri'] = '%s/%s' % (settings.get('host').rstrip('/'), settings.get('redirect_uri').lstrip('/'))
else:
    import tornado.web
    import yaml

    if not settings.get('database_dialect'):
        # 设置默认数据库
        settings['database_dialect'] = 'sqlite:///%s' % os.path.join(os.getcwd(), 'db.sqlite')

    # 处理静态文件.
    config_yaml = open('config.yaml')
    for handler in yaml.load(config_yaml).get('handlers', []):
        if handler.get('static_dir'):
            urls.insert(0, (r'%s/(.*)' % handler.get('url').rstrip('/'), tornado.web.StaticFileHandler, {'path': handler.get('static_dir')}))

    # 处理SAE的回调地址
    settings['host'] = '%s:%s' % (settings.get('localhost'), settings.get('port'))
    settings['redirect_uri'] = '%s/%s' % (settings.get('host').rstrip('/'), settings.get('redirect_uri').lstrip('/'))

    tornado_app = tornado.web.Application(urls, **settings)
    tornado_app.listen(settings.get('port'))


# 数据库初始化. 
db.config(settings.get('database_dialect'), settings.get('debug', False))
db.create_all()


if is_sae:
    import sae
    import tornado.wsgi
    tornado_app = tornado.wsgi.WSGIApplication(urls, **settings)
    application = sae.create_wsgi_app(tornado_app)

# 方便本地命令行调试, python3 index.wsgi shell
if len(sys.argv)>1 and sys.argv[1].strip()=='shell':
    import code
    #interp = code.InteractiveConsole({'s':10}).interact("")
    code.interact('\nWelcome to KissWeb shell...\n')
elif not is_sae:
    import tornado.ioloop
    tornado.ioloop.IOLoop.instance().start()
