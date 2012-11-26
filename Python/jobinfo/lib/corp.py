# coding=utf8

from opener import Opener
from funcs import coroutine
from funcs import get_cst
import logging, time, datetime, itertools, multiprocessing

logging.basicConfig(format='[%(asctime)s] %(message)s')

class Corp(multiprocessing.Process):
    def __init__(self, corplist_url, corp_url, info_from, corplist_post_data=None, corp_post_data=None, corplist_reg=None, corp_regs=[], timeout=5, commit_each_times=30, has_cookie=True, charset='utf8', model=None):
        """ 参数 corplist_url 和 corp_url 取胜字符串的高级格式化:format, 使用{0},{1}等通配符; """
        super().__init__()
        self.charset = charset
        self.info_from = info_from
        self.corplist_url = corplist_url
        self.corp_url = corp_url
        self.opener = Opener(has_cookie=has_cookie, encoding=self.charset)

        self.corplist_post_data = corplist_post_data
        self.corp_post_data = corp_post_data
        self.corplist_reg = corplist_reg
        self.corp_regs = corp_regs
        self.commit_each_times = commit_each_times
        self.timeout = timeout

        if model:
            self.model = model
        else:
            from lib.models import CorpModel
            self.model = CorpModel

        #self._today = get_cst()
        self._today = datetime.date.today()

    def _msg(self, msg=''):
        #print('%s %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg))
        logging.info(msg)

    def set_queue(self, queue):
        self.queue = queue


    def process_corp_info(self, corp_info, date_reg=r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'):
        for key, values in corp_info.items():
            corp_info[key] = values.strip()
        if 'insert_date' in corp_info:
            corp_info['insert_date'] = self.model._str2date(corp_info['insert_date'], date_reg=date_reg)
        else:
            corp_info['insert_date'] = self._today
        return corp_info

    def get_next_page_url(self):
        """ 必须是一个非协程的Generator, 或者返回一个iterable. """
        return (self.corplist_url)

    def get_corp_url(self, corp_info={}):
        return self.corp_url.format(**corp_info)

    def prepare(self):
        pass

    def fetch_corplist(self, page_url):
        """ 如果成功抓取, 返回一个包含 Corp Info dict 的列表或者iterable; 否则返回 {}. """
        content = self.opener.urlopen(page_url, data=self.corplist_post_data, timeout=self.timeout, times=0)
        return ({} if not search_obj else search_obj.groupdict() for search_obj in self.corplist_reg.finditer(content))

    def fetch_corp(self, corp_info=None):
        """ 如果成功抓取, 返回一个Corp Info 的 dict. """
        corp_url = self.get_corp_url(corp_info)
        content = self.opener.urlopen(corp_url, data=self.corp_post_data, timeout=self.timeout, times=0)
        for reg in self.corp_regs:
            search_obj = reg.search(content)
            search_obj and corp_info.update(search_obj.groupdict())
        return corp_info

    def before_save(self, corp_info):
        corp_info = self.process_corp_info(corp_info)
        corp_info['info_from'] = self.info_from
        return corp_info

    def commit(self):
        self.model.commit()

    @coroutine
    def check_exists(self):
        """ 存在的话返回其 info_from, 否则返回 None. """
        corp_names_cache = {}
        corp_names_cache_list = []
        cache_length = 0
        result = None
        while 1:
            corp_info = (yield result)
            result = None
            corp_name = corp_info['name'].strip()
            if corp_name not in corp_names_cache:
                corp_names_cache[corp_name] = self.info_from
                corp_names_cache_list.insert(0,corp_name)
                cache_length += 1
                if cache_length > self.commit_each_times:
                    del corp_names_cache[corp_names_cache_list.pop()]
                    cache_length -= 1
                exists_corp = self.model.filter_by(name=corp_name).first()
                if exists_corp:
                    result = exists_corp.info_from
                    corp_names_cache[corp_name] = result
            else:
                result = corp_names_cache[corp_name]

    def run(self):
        self.prepare()
        check_exists = self.check_exists()
        cur_page = itertools.count()
        for page_url in self.get_next_page_url():
            print('\n%s 第%s页' % (self.info_from, next(cur_page)+1))
            for corp_info in self.fetch_corplist(page_url):
                self._msg('***************************************************')
                print(corp_info['name'], end=' ')
                info_from = check_exists.send(corp_info)
                if not info_from:
                    corp_info = self.fetch_corp(corp_info)
                    corp_info = self.before_save(corp_info)
                    self.queue.put(corp_info)
                else:
                    print('已经存在于: %s' % info_from)
        self._msg('\n%s 抓取完毕!' % self.info_from)
        self.queue.put(None)

    def report(self, fields=None):
        corps = self.model.filter_by(info_from=self.info_from, insert_date=datetime.date.today())
        #corps = self.model.filter_by(info_from=self.info_from, insert_date=datetime.date(2011,12,8))
        fields = fields or (
            ('名称', 'name'),
            ('地址', 'addr'),
            ('联系人', 'contact_person'),
            ('区号', 'contact_tel_code'),
            ('电话号码', 'contact_tel_no'),
            ('邮箱', 'mail'),
            ('网址', 'website'),
            ('信息来源', 'info_from'),
            ('更新日期', 'insert_date'),
            ('链接', self.corp_url),
        )
        self.model.report('%s最新公司信息_%s.csv' % (self.info_from, time.strftime('%Y-%m-%d')), fields=fields, rows=corps, encoder='gbk')



class Commiter(multiprocessing.Process):
    """ 查询或者插入数据. """
    def __init__(self, queue, db_lock, process_num, model=None, commit_each_times=30):
        super().__init__()
        if model:
            self.model = model
        else:
            from lib.models import CorpModel
            self.model = CorpModel
        self.queue = queue
        self.db_lock = db_lock
        self.process_num = process_num
        self._over_times = 0
        self._cache = set()
        self._add_times = 0
        self.commit_each_times = commit_each_times

    def is_over(self):
        """ 所有processes全结束才返回true. """
        return self._over_times>=self.process_num

    def save(self, corp_info):
        corp_name = corp_info.get('name').strip()
        if corp_name in self._cache:
            return
        #with self.db_lock:
        self.model.add(corp_info, is_commit=False)
        self._cache.add(corp_name)
        self._add_times += 1
        if self._add_times % self.commit_each_times == 0:
            self.model.commit()

    def run(self):
        while 1:
            corp_info = self.queue.get()
            if corp_info is None:
                self._over_times += 1
                if self.is_over():
                    """ 当接受到None数据, 并且所有processes结束, 此process才结束. """
                    self.model.commit()
                    return 0
                continue
            self.save(corp_info)
