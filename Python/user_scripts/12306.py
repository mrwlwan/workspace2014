# coding=utf8

import requests
from http.cookiejar import LWPCookieJar
import os, sys, logging, getpass, time, collections, json, subprocess, re, itertools, winsound, pickle
import urllib.parse

logging.basicConfig(format='%(message)s', level=logging.INFO)

SEAT_CLASS = collections.OrderedDict([('gb', '商务座'), ('gs', '特等座'), ('g1', '一等座'), ('g2', '二等座'), ('s1', '高级软卧'), ('s2', '软卧'), ('s3', '硬卧'), ('1', '软座'), ('2', '硬座'), ('3', '无座'), ('4', '其他')])

TRAIN_CLASS = collections.OrderedDict([
    ('QB', ('QB#D#Z#T#K#QT#', '全部')),
    ('D', ('D#', '动车')),
    ('Z', ('Z#', '直特')),
    ('T', ('T#', '特快')),
    ('K', ('K#', '快速')),
    ('QT', ('QT#', '其它')),
])


class OptionValue:
    def __init__(self, value, verbose=None):
        self.value = value
        self.verbose = value if verbose is None else verbose

    def __str__(self):
        return self.verbose


class Options:
    STATION_NAME_STRING = None

    def __init__(self, save_path='saved'):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        self.save_path = save_path
        self.operations = [
            {'name': '执行', 'method': None},
            {'name': '修改查询参数', 'method': self.change},
            {'name': '保存查询参数', 'method': self.save},
            {'name': '加载查询参数', 'method': self.load},
            {'name': '删除保存的配置', 'method': self.delete},
            {'name': '显示查询参数', 'method': lambda: print(self.to_query('query'), '\n', self.to_querystring('query'))},
        ]
        self.data = {
            'query': collections.OrderedDict([
                # 没有choices属性的放在最后
                ('orderRequest.from_station_telecode',
                    {'name': '出发地', 'value': OptionValue(''), 'choices': self.input_station_name, 'order': 2}
                ),
                ('orderRequest.to_station_telecode',
                    {'name': '目的地', 'value': OptionValue(''), 'choices': self.input_station_name, 'order': 3}
                ),
                ('orderRequest.train_date',
                    {'name': '出发日期', 'value': OptionValue(time.strftime('%Y-%m-%d')), 'choices': self.input_date, 'order': 1}
                ),
                ('orderRequest.start_time_str',
                    {'name': '出时时间', 'value': OptionValue('00:00--24:00'), 'choices': ('00:00--24:00', '00:00--06:00', '06:00--12:00', '12:00--18:00', '18:00--24:00'), 'order': 9}
                ),
                ('trainClass',
                    {'name': '列车型号', 'value': OptionValue('QB#D#Z#T#K#QT#', '全部'), 'choices': self.input_train_class, 'order': 6}
                ),
                ('trainPassType',
                    {'name': '路线类型', 'value': OptionValue('QB', '全部'), 'choices': (('QB', '全部'), ('SF', '始发'), ('LG', '过路')), 'order': 5}
                ),
                ('includeStudent',
                    {'name': '学生票', 'value': OptionValue('00', '否'), 'choices': (('00', '否'), ('0X00', '是')), 'order': 7}
                ),
                ('orderRequest.train_no',
                    {'name': '车次', 'value': OptionValue(''), 'order': 4}
                ),
                ('seatTypeAndNum',
                    {'name': '座号', 'value': OptionValue(''), 'order': 8}
                ),
            ]),
            'limited': collections.OrderedDict([
                ('nos',
                    {'name': '指定车次', 'value': OptionValue('', '不限'), 'choices': self.input_nos, 'filter': self.nos_filter},
                ),
                ('seats',
                    {'name': '指定座位类型', 'value': OptionValue('seat_1', '硬座'), 'choices': self.input_seats, 'filter': self.seats_filter},
                ),
                ('interval',
                    {'name': '刷新时间', 'value': OptionValue(10.0, '10秒'), 'choices': self.input_interval},
                ),
            ]),
        }
        self._success = False

    @property
    def is_success(self):
        """ 判断是否找到相应的票. """
        return self._success

    @property
    def station_name_string(self):
        if not Options.STATION_NAME_STRING:
            Options.STATION_NAME_STRING = self.get_station_name_string()
        return Options.STATION_NAME_STRING

    def _input(self, *args, title='可选择操作'):
        length = [len(option_titles) for option_titles in args]
        length_cmp = []
        for i in range(len(length)):
            if i == 0:
                length_cmp.append(length[i])
            else:
                length_cmp.append(length_cmp[i-1]+length[i])
        while 1:
            print('\n{0}: '.format(title))
            for option_title in enumerate(itertools.chain(*args), 1):
                print('{0}.{1}'.format(*option_title))
            try:
                select = input('请选择: ').strip()
                if not select: return None
                select = int(select)
                if select<1 or select>length_cmp[-1]: raise Exception('超出选择范围!')
                break
            except:
                print('无效选择!')
                continue
        result = []
        temp_length = len(length_cmp)
        for i in range(len(length_cmp)):
            if i==0:
                result.append(select-1 if select<=length_cmp[i] else None)
            else:
                result.append(select-length_cmp[i-1]-1 if length_cmp[i-1]<select<=length_cmp[i] else None)
        return result

    def get_station_name_string(self):
        """ 返回火车站点查询字符串."""
        return  re.search(r"""['"]([^'"]+)""", requests.get('http://dynamic.12306.cn/otsweb/js/common/station_name.js').content.decode('utf8')).group(1)

    def query_station_name(self, query):
        reg = re.compile(r'@[^\|]+[^@]*?\|{0}[^@]+'.format(query), re.I)
        options = []
        for item in reg.findall(self.station_name_string):
            temp = item.split('|')
            options.append((temp[2], temp[1]))
        if not options:
            print('未查询到结果')
            return None
        titles = [item[1] for item in options]
        select = self._input(titles)
        if select:
            return OptionValue(*options[select[0]])
        else:
            return None

    def input_station_name(self):
        while 1:
            query = input('\n请输入站点名或者拼音(简写): ').strip()
            if not query: return None
            value = self.query_station_name(query)
            if value is not None:
                return value

    def input_date(self):
        while 1:
            date = input('\n请输入出发日期(格式xxxx-xx-xx): ').strip()
            if not date: return None
            if re.match(r'^\d{4}-\d{2}-\d{2}$', date):
                return OptionValue(date)
            print('日期格式有误!')

    def input_train_class(self):
        """ 输入车型. """
        while 1:
            items = input('\n请输入列车类型(QB[全部]/D[动车]/Z[直特]/T[特快]/K[快速]/QT[其它]), 多类型逗号分隔:\n').strip().upper()
            if not items:
                return None
            items = set(re.split(r'[\s,]+', items))
            if [item for item in items if item not in TRAIN_CLASS]:
                print('无效输入!')
                continue
            temp = collections.OrderedDict.fromkeys(TRAIN_CLASS.keys(), '')
            for item in items:
                if item=='QB':
                    return OptionValue(TRAIN_CLASS.get('QB')[0], '全部')
                temp[item] = TRAIN_CLASS.get(item)[0]
            return OptionValue(''.join(temp.values()), '/'.join([TRAIN_CLASS.get(key)[1] for key, value in temp.items() if value]))

    def input_nos(self):
        """ 限定车次."""
        items = input('\n请指定车次, 多个车次以逗号分隔: ').strip().upper()
        if not items:
            return None
        items = set(re.split(r'[\s,]+', items))
        return OptionValue(items, '/'.join(items))

    def input_seats(self):
        """ 限定座位类型(和数量). """
        REG = re.compile(r'(?:gb|gs|g1|g2|s1|s2|s3|1|2|3|)(?:\(\d+\))?$', re.I)
        while 1:
            seats = input('\n请指定座位类型(GB[商务座]/GS[特等座]/G1[一等座]/G2[二等座]/S1[高级软卧]/S2[软卧]/S3[硬卧]/1[软座]/2[硬座]/3[无座]/4[其他]), 多个类型以逗号分隔:\n').replace(' ', '').lower()
            if not seats:
                return None
            items = set(re.split(r'[\s,]+', seats))
            temp = collections.OrderedDict.fromkeys(SEAT_CLASS.keys(), '')
            result = []
            for item in items:
                if not REG.match(item):
                    print('输入有误!')
                    continue
                result.append('seat_{0}'.format(item))
                temp[item] = SEAT_CLASS.get(item)
            return OptionValue(result, '/'.join([value for value in temp.values() if value]))

    def input_interval(self):
        """ 指定刷新时间. """
        while 1:
            interval = input('请输入时间(秒): ').strip()
            if not interval:
                return None
            try:
                return float(interval)
                print('设置刷新时间成功!')
                break
            except:
                print('输入有误!')

    def change(self):
        query_options = [value for value in self.data.get('query').values() if 'choices' in value]
        limited_options = list(self.data.get('limited').values())
        while 1:
            query_titles = ['{0}({1})'.format(item.get('name'), item.get('value')) for item in query_options]
            limited_titles = ['{0}({1})'.format(item.get('name'), item.get('value')) for item in limited_options]
            select = self._input(query_titles, limited_titles, title='可修改参数列表')
            if select is None:
                return
            select, options = (select[0], query_options) if select[0] is not None else (select[1], limited_options)
            choices = options[select].get('choices')
            if isinstance(choices, tuple):
                value = self.choice(choices)
            elif callable(choices):
                value = choices()
            if value is not None:
                options[select]['value'] = value

    def choice(self, choices):
        items = [(item[0], item[1]) if isinstance(item, tuple) else (item, item) for item in choices]
        item_titles = [item[1] for item in items]
        select = self._input(item_titles)
        if select is not None:
            return OptionValue(*items[select[0]])
        return None

    def get(self, option_type, option_name=None, key='value'):
        option_dict = self.data.get(option_type)
        if option_name:
            return option_dict.get(option_name).get(key)
        else:
            return [value.get(key) for value in option_dict.values()]

    def set(self, option_type, option_name, value, key='value'):
        self.data.get(option_type)[option_name][key] = value

    def _sorted_query(self, item):
        """ 排序query. """
        return item[1].get('order')

    def to_query(self, option_type, sort=False):
        """ 返回查询字典. """
        items = self.data.get(option_type).items()
        if sort:
            items = sorted(items, key=self._sorted_query)
        return [(key, value.get('value').value) for key, value in items]

    def to_querystring(self, option_type):
        """ 返回查询字符串. """
        return urllib.parse.urlencode(self.to_query(option_type))

    def as_dict(self):
        """ 简单dict对象. 用于pickle. """
        result = {}
        for key, value in self.data.items():
            result[key] = {}
            for i, j in value.items():
                result[key][i] = j.get('value')
        return result

    def operate(self):
        while 1:
            option_titles = [item.get('name') for item in self.operations]
            select = self._input(option_titles, title='可选操作')
            if select:
                method = self.operations[select[0]].get('method')
                if method:
                    method()
                else:
                    return

    def _select_filenames(self, title='可选配置文件'):
        """ 选择配置文件. """
        filenames = [filename for filename in os.listdir(self.save_path) if os.path.isfile(os.path.join(self.save_path, filename))]
        select = self._input(filenames, title=title)
        return select and os.path.join(self.save_path, filenames[select[0]])

    def load(self):
        """ 加载配置文件. """
        while 1:
            filepath = self._select_filenames()
            if filepath is not None:
                try:
                    with open(filepath, 'rb') as f:
                        a = pickle.load(f)
                        for key, value in a.items():
                            for i, j in value.items():
                                self.set(key, i, j)
                    print('加载成功!')
                    break
                except:
                    print('加载失败!')

    def save(self):
        """ 保存参数为配置文件. """
        while 1:
            filename = input('请输入文件名: ').strip()
            if not filename:
                return
            filepath = os.path.join(self.save_path, filename)
            if os.path.exists(filepath):
                check = input('文件已经存在, 覆盖(y/n)? ').strip().lower()
                if not check=='y':
                    continue
            try:
                with open(filepath, 'wb') as f:
                    pickle.dump(self.as_dict(), f)
                print('保存成功!')
                break
            except:
                print('保存失败!')

    def delete(self):
        """ 删除配置文件. """
        while 1:
            filepath = self._select_filenames()
            if filepath is None: break
            try:
                os.remove(filepath)
                print('删除成功!')
                break
            except:
                print('删除失败!')

    def nos_filter(self, row):
        """ 过滤车次. """
        nos = self.get('limited', 'nos').value
        if not nos:
            return row
        return row if row.get('no') in nos else None

    def seats_filter(self, row):
        """ 过滤座位类型. """
        self._success = False
        seats = self.get('limited', 'seats').value
        if seats:
            for seat in seats:
                if Seat(row[seat]).has_tickets():
                    self._success = True
                    break
        return row

class Seat:
    def __init__(self, data):
        self.data = data

    def has_tickets(self):
        return self.data.isdigit() or self.data.find('有')>=0

    def get_num(self):
        if self.data.isdigit():
            return int(self.data)
        elif self.data.find('有'):
            return '大量'
        else:
            return 0

class Ticket:
    ROW_REG = re.compile(r"(?P<index>\d+),<span id=[^>]+>(?P<no>[^<]+)</span>,(?:<[^>]+>)?(?:&nbsp;)+(?P<from>[^&]+)[^\d]+(?P<start>[\d:]+),(?:<[^>]+>)?(?:&nbsp;)+(?P<to>[^&]+)[^\d]+(?P<end>[\d:]+),(?P<detal>[\d:]+),(?:<[^>]+>)?(?P<seat_gb>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_gs>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_g1>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_g2>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_s1>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_s2>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_s3>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_1>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_2>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_3>[^<,]+)(?:[^,]*),(?:<[^>]+>)?(?P<seat_4>[^<,]+)(?:[^,]*),")

    def __init__(self, username, password=None, cookie_dir='cookies'):
        self.username = username
        self.password = password
        self.cookie_path = os.path.join(cookie_dir, '{0}.txt'.format(username))
        self.session = requests.Session()
        cookiejar = LWPCookieJar(self.cookie_path)
        if os.path.exists(self.cookie_path):
            cookiejar.load()
        self.session.cookies = cookiejar
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20130110 Firefox/21.0'
        self.session.headers['Referer'] = 'http://dynamic.12306.cn/otsweb/order/querySingleAction.do?method=init'
        self.urlget = self.session.get
        self.urlpost = self.session.post
        self.query = Options()

    @property
    def is_success(self):
        """ 是否找到票. """
        return self.query.is_success

    def check_login(self, content):
        if content.find('我的12306')>=0:
            return True
        return False

    def fetch_logincode(self, saved='code.jpg'):
        login_code_url = 'http://dynamic.12306.cn/otsweb/passCodeAction.do?rand=sjrand'
        with open(saved, 'wb') as f:
            f.write(self.urlget(login_code_url).content)
        subprocess.Popen('rundll32.exe shimgvw.dll,ImageView_Fullscreen '+os.path.abspath(saved))

    def login(self):
        login_page_url = 'http://dynamic.12306.cn/otsweb/loginAction.do?method=init'
        login_preurl = 'http://dynamic.12306.cn/otsweb/loginAction.do?method=loginAysnSuggest'
        login_url = 'http://dynamic.12306.cn/otsweb/loginAction.do?method=login'
        data = {
            'loginUser.user_name': self.username,
            'randCode': '',
            'user.password': '',
            'refundLogin': 'N',
            'refundFlag': 'Y',
            'randErrorFocus': '',
            'passwordErrorFocus': '',
            'nameErrorFocus': '',
            'loginRand': '',
        }
        self.urlget(login_page_url)
        while 1:
            self.fetch_logincode()
            print('\n请输入:')
            if not self.password:
                self.password = getpass.getpass('[密码]').strip()
                if not self.password:
                    continue
            code = input('[验证码]').strip()
            if not code:
                continue
            data.update(self.urlpost(login_preurl).json())
            data.update({
                'user.password': self.password,
                'randCode': code,
            })
            content = self.urlpost(login_url, data).text
            if self.check_login(content):
                self.msg('登录成功!')
                self.session.cookies.save()
                break

    def change_query(self):
        self.query.operate()

    def parse(self, content):
        return [search_obj.groupdict() for search_obj in self.ROW_REG.finditer(content)]

    def action(self):
        limited_filters = self.query.get('limited', key='filter')
        params = self.query.to_query('query', True)
        #line_spliter = '\n{0}'.format('='*80)
        line_spliter = '\n'
        g_format = '{no:6} {from}({start})--{to:}({end}) 历时({detal})\n       商务座({seat_gb}) 特等座({seat_gs}) 一等座({seat_g1}) 二等座({seat_g2})'
        s_format = '{no:6} {from:}({start})--{to:}({end}) 历时({detal})\n       高级软卧({seat_s1}) 软卧({seat_s2}) 硬卧({seat_s3}) 软座({seat_1}) 硬座({seat_2}) 无座({seat_3})'
        while 1:
            query_url = 'http://dynamic.12306.cn/otsweb/order/querySingleAction.do?method=queryLeftTicket'
            content = self.urlget(query_url, params=params).text
            rows = self.parse(content)
            temp_rows = []
            for row in rows:
                for limited_filter in limited_filters:
                    if callable(limited_filter):
                        row = limited_filter(row)
                        if not row: break
                if row: temp_rows.append(row)
            rows = temp_rows
            if not rows:
                print('未找到符合条件的列车')
                return
            self.msg('')
            print(line_spliter.join([(re.match(r'G|D', row.get('no')) and g_format or s_format).format(**row) for row in rows]))
            if self.is_success:
                print('找到车票')
                winsound.Beep(321, 64)
                sys.exit();
            else:
                print('未找到车票')
            print()
            time.sleep(self.query.get('limited', 'interval'))

    def msg(self, message):
        """ 显示信息. """
        logging.info('[{0}][{1}] {2}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), self.username, message))

    def test(self, text, filename='page.html'):
        with open(filename, 'w', encoding='utf8') as f:
            f.write(text)

if __name__ == '__main__':
    ticket = Ticket('mrwlwan')
    ticket.login()
    ticket.change_query()
    ticket.action()
