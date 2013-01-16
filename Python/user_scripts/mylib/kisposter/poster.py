# coding=utf8

import requests, lxml.html, lxml.etree
from http.cookiejar import LWPCookieJar
import urllib.parse, os.path, sys, logging, getpass, time, datetime, re

logging.basicConfig(format='%(message)s', level=logging.INFO)


class DateTimeString:
    """ Datetime 和 String 的结合. """
    def __init__(self, datetime=None, datetime_string=None, format='%Y-%m-%d %H:%M:%S'):
        """ '必须设置datetime或者datetime_string参数之一, 两者皆设则只认datetime. """
        if datetime:
            self.__datetime = datetime
            self.__datetime_string = None
        elif datetime_string:
            self.__datetime_string = datetime_string
            self.__datetime = None
        else:
            raise Exception('必须设置datetime或者datetime_string参数之一')
        self.__format = format

    @property
    def datetime(self):
        if not self.__datetime:
            self.__datetime = datetime.datetime.strptime(self.__format)
        return self.__datetime

    @property
    def string(self):
        if not self.__datetime_string:
            self.__datetime_string = datetime.datetime.strftime(self.__format)
        return self.__datetime_string

    def __str__(self):
        return self.string


class Helper:
    """ 辅助类. """
    CHARSET_REG = re.compile(r'charset=["\']?([^"\']+)')

    def __init__(self, domain, session=None):
        self.domain = domain
        self.session = session or request.session()
        self.caches = {}
        self.urlget = self.session.get
        self.urlpost = self.session.post

    def get_absolute_url(self, url):
        """ 返回绝对地址. """
        return urllib.parse.urljoin(self.domain, url)

    def get_charset(self):
        """ 取得页面charset. """
        if not self.caches.get('charset'):
            if not self.caches.get('home_page'):
                self.caches['home_page'] = self.urlget(self.domain)
            search_obj = self.CHARSET_REG.search(self.caches.get('home_page'))
            self.caches['charset'] = search_obj.group(1) if search_obj else 'utf8'
        return self.caches.get('charset')

    def parse_url_query(self, url, encoding=None):
        """ 分析Url Queries. """
        url = urllib.parse.unquote(url, encoding or self.get_charset())
        query = urllib.parse.urlparse(url).query
        return dict([(key, len(value)>1 and value or value[0]) for key, value in urllib.parse.parse_qs(query)])



class Poster:
    """ 基础类. 提供逻辑流程. """
    REQUIRE_OPTIONS = set(['username', 'domain'])
    def __init__(self, **kwargs):
        """ 必填参数: domain, username, check_login_url, check_login_target,

        """
        self._require_options(kwargs.keys())
        self.options = kwargs
        self.username = self.options.get('username')
        self.domain = self.options.get('domain')
        cookies_path = self.options.get('cookies_path')
        cookiejar = LWPCookieJar(cookies_path)
        if cookies_path and os.path.exists(cookies_path):
            cookiejar.load()
        self.session = requests.Session()
        self.session.cookies = cookiejar
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130110 Firefox/21.0'
        self.session.headers.update(self.options.get('headers', {}))
        self.urlget = self.session.get
        self.urlpost = self.session.post
        self.helper = Helper(self.domain, session=self.session)

    def _require_options(self, options_names):
        lost_options = self.REQUIRE_OPTIONS - set(options_names)
        if lost_options:
            raise Exception('缺少参数: %s' % ', '.join(lost_options))

    def _url(self, url):
        """ 返回绝对地址. 便捷函数. """
        return self.helper.get_absolute_url(url)

    def _datetime(self, datetime_string):
        """ 返回datetime类型. """
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')

    def msg(self, message):
        """ 显示信息. """
        logging.info('[{0}][{1}] {2}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), self.username, message))

    def save_cookies(self, cookie_path=None):
        """ 保存cookies到文件. """
        if cookie_path or self.session.cookies.filename:
            self.session.cookies.save(cookie_path or None)

    def get_timeout(self):
        """ 返回Request timeout. """
        return self.options.get('timeout')

    def get_form_data(self, form, default=''):
        """ 返回form数据, None自动转化为default值. """
        return dict(((key, value if value is not None else default) for key, value in form.fields.items()))

    def get_login_page_url(self):
        """ 返回login_page_url. 绝对地址! """
        return self._url(self.options.get('login_page_url'))

    def get_login_form_url(self):
        """ 返回login_form_url. 绝对地址! """
        return self._url(self.options.get('login_form_url') or '/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LBnCh&inajax=1')

    def get_check_login_url(self):
        """ 返回check_login_url. 绝对地址! """
        return self._url(self.options.get('check_login_url'))

    def get_check_login_target(self):
        """ 返回check_login_target. 绝对地址! """
        return self.options.get('check_login_target')

    def get_login_data(self, data=None):
        """ 返回check_login_target. 绝对地址! """
        root = lxml.html.parse(self.get_login_page_url())
        forms = root.xpath('//form[contains(@action, "login")]')
        if forms:
            temp = self.get_form_data(forms[0])
            temp.update(self.options.get('login_data', {}))
            data and temp.update(data)
            return temp
        else:
            self.msg('未找到登录表单')
            sys.exit()

    def extra_login_data(self, data=None):
        """ Cookie登录失败后输入的登录数据. 返回一个dit对象. """
        print('登录名: {0}'.format(self.username))
        password = getpass.getpass('密码: ')
        temp = {'username': self.username, 'password': password or ''}
        data and temp.update(data)
        return temp

    def check_login(self, content=None):
        """ 检查是否登录成功. """
        content = content or self.urlget(self.get_check_login_url()).text
        if content.find(self.get_check_login_target())>=0:
            return True
        return False

    def login(self, **kwargs):
        """ 登录. """
        if self.check_login():
            self.msg('Cookies 登录成功!')
            return True
        data = self.get_login_data()
        data.update(self.extra_login_data())
        data.update(kwargs)
        response = self.urlpost(self.get_login_form_url(), data)
        if self.check_login(response.text):
            self.msg('登录成功')
            self.save_cookies()
            return True
        else:
            self.msg('登录失败')
            return False

    def get_thread_url(self):
        """ 返回帖子URL. """
        return self._url(self.options.get('thread_url'))

    def get_post_url(self):
        """ 返回POST Form Url. """
        return self._url(self.options.get('post_url'))

    def get_post_data(self, data=None):
        """ 返回post_data. """
        temp = self.options.get('post_data', {})
        data and temp.update(data)
        return temp

    def get_post_headers(self, headers=None):
        """ 返回POST Headers. """
        temp = self.options.get('post_headrs')
        headers and temp.update(headers)
        return temp

    def get_post_cookies(self, cookies=None):
        """ 返回POST Cookies. """
        temp = self.options.get('post_cookies')
        cookies and temp.update(cookies)
        return temp

    def get_post_timeout(self):
        """ 返回POST Timeout. """
        return self.options.get('post_timeout', self.get_timeout())

    def before_post(self):
        """ 发表内容之前. 返回一个POST Date dict 对象. """
        return {}

    def after_post(self, response):
        """ 发表内容之后. """
        pass

    def post(self, url=None, data=None, headers=None, cookies=None, timeout=None):
        """ 发表内容. """
        self.before_post()
        url = url or self.get_post_url()
        data = self.get_post_data(data)
        response = self.urlpost(url or self.get_post_url(), data or self.get_post_data(), headers=headers or self.get_post_headers(), cookies=cookies or self.get_post_cookies(), timeout=timeout or self.get_post_timeout())
        self.after_post(response)

    def action(self):
        """ 循环执行. """
        pass
