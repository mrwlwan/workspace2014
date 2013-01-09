# coding=utf8

from webkiss.utils import is_sae
from webkiss.loader import JinjaLoader
from taobao.shop.urls import urls as tbs_urls
from home.urls import urls as home_urls

jinja_loader = JinjaLoader('templates')
jinja_loader.config_env(
    trim_blocks=True
)


# wsgi application setting. 如果是SAE应用, 请不要在此处设置 static_path和static dir 请在 config.yaml 指定.
settings = {
    # 下面是 tornado 设置
    'template_path': 'templates',
    'template_loader': jinja_loader,
    'filters': {},
    'globals': {},
    'cookie_secret': 'mrwlwan#gmail.comsaeweiliangwan81',
    'xsrf_cookies': True,
    # 下面是 sae 和 weibo 参数
    'title': 'Ross Wan\'s World!',
    'host': 'http://mrwlwan.sinaapp.com',
    'app_key': '2247438201',
    'app_secret': 'cd27dd2a2a8c198b9eecd091c57cd9bb',
    'redirect_uri': '/login', # 填相对地址
    # 下面是本地调试设置
    'debug': True,
    'localhost': 'http://localhost',
    'port': 8080,
}

# url 映射规则. 如果是SAE应用, static handler 不要显式指定, 在config.yaml里进行设定.
#from home.home import HomeHandler
urls = [
    (r'/?$', home_urls),
    (r'^/taobao/shop/redirect', tbs_urls),
]
