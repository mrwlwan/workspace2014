# coding=utf8

from webkiss.utils import is_sae
from home.urls import urls as home_urls

# wsgi application setting. 如果是SAE应用, 请不要在此处设置 static_path和static dir 请在 config.yaml 指定.
settings = {
    # 下面是 tornado 设置
    'template_path': 'templates',
    'cookie_secret': 'mrwlwan#gmail.comsaeweiliangwan81',
    'xsrf_cookies': True,
    # 下面是 sae 和 weibo 参数
    'title': 'Ross Wan\'s World!',
    'host': 'http://mrwlwan.sinaapp.com',
    'app_key': '2247438201',
    'app_secret': '',
    'redirect_uri': '/login', # 填相对地址
    # 下面是本地调试设置
    'debug': True,
    'localhost': 'http://localhost',
    'port': 8080,
}

# url 映射规则. 如果是SAE应用, static handler 不要显式指定, 在config.yaml里进行设定.
urls = [
    #(r'/$', home.HomeHandler),
    (r'/', home_urls),
]
