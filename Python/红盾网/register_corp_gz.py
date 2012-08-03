#! urs/bin/python3
# coding=utf8

from opener import Opener
from lib.models_gz import CorpModel, InvalidCodeModel, MaxCodeModel
from functools import reduce
from funcs import get_cst
import re, logging, os, datetime, time, sys

class Register_corp:
    def __init__(self):
        logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
        self.model = CorpModel
        self.invalid_code_model = InvalidCodeModel
        self.max_code_model = MaxCodeModel
        self.info_from = '广东红盾网'
        self.charset = 'utf8'
        self.opener = Opener(has_cookie=True, encoding=self.charset)
        # 6位机关代码; 6位
        self.org_code = '440101'
        # 企业性质号码; 2位, 00~30为内资;40~50为外资.
        self.nature_num = 0
        # 流水号; 4位
        self.ord_num= 0
        self.query_url = 'http://www.gzaic.gov.cn/gsbm/FrmRegBaseopeninfo.aspx'
        self.corp_url = 'http://www.gzaic.gov.cn/gsbm/FrmRegBaseOpeninfoDetail.aspx?key={0}'
        self.search_string = '查看'
        self.reg = re.compile(r'lbSREGNO">(?P<register_code>[^<]*)</span></td>.*?lbSNAME">(?P<name>[^<]*)</span></td>.*?lbSDOM">(?P<addr>[^<]*)</span></td>.*?lbSMAN">(?P<representative>[^<]*)</span></td>.*?lbSENTCLASS">\s*(?P<nature>[^<]*)</span></td>.*?lbSREGCAP">(?P<capital>[^<]*)</span></td>.*?lbSSSZB">[^<]*</span></td>.*?lbSOPSCOPE">(?P<scope>[^<]*)</span></td>.*?LbSREGRDATE">(?P<establishment_data>[^<]*)</span></td>.*?lbSAPPRDATE">[^<]*</span></td>.*?lbSREGORG">(?P<register_department>[^<]*)</span></td>', re.S)
        self.event_regs = [
            re.compile(r'__VIEWSTATE" value="(?P<__VIEWSTATE>[^"]*)'),
            re.compile(r'__EVENTVALIDATION" value="(?P<__EVENTVALIDATION>[^"]*)'),
        ]
        self.key_reg = re.compile(r'key=(?P<key>[^\']*)')
        self.post_data = {
            '__EVENTTARGET': 'QueryButton',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            '__EVENTVALIDATION': '',
            'txtName': '',
            'txtReg': '',
        }

        self._save_times = 0
        self._today = get_cst()

        self.initial()

    # 初始化 ufps
    def initial(self):
        self.fetch_content(self.query_url)

    def _msg(self, text):
        return '%s %s' % (time.asctime(), text)

    def _process(self, corp_dict):
        corp_dict.update({
            'insert_date': self._today,
            'info_from': self.info_from,
            'status': '登记成立',
            'period': '长期',
        })
        if 'establishment_data' in corp_dict and corp_dict['establishment_data']:
            corp_dict['establishment_data'] = self.model._str2date(corp_dict['establishment_data'])
        return corp_dict

    def calc_code15(self, org_code, nature_num, ord_num):
        """ 计算15位注册号的检验码. 并返回15位注册号. """
        code14 = '%s%02d%06d' % (org_code, nature_num, ord_num)
        temp =  reduce(lambda x,y: ((x+int(y))%10 or 10)*2%11, code14, 10)
        return '%s%s' % (code14, (11-temp)%10)

    def update_events(self, content):
        for reg in self.event_regs:
            search_obj = reg.search(content)
            search_obj and self.post_data.update(search_obj.groupdict())

    def fetch_content(self, url, data=None, timeout=10, raw_string=False, update_events=True):
        content = self.opener.urlopen(url, data, timeout=timeout, times=0)
        update_events and self.update_events(content)
        return content

    def fetch_query_content(self, code):
        self.post_data.update({
            '__EVENTTARGET': 'QueryButton',
            'txtReg': code,
        })
        return self.fetch_content(self.query_url, self.post_data)

    def fetch_key_content(self):
        self.post_data['__EVENTTARGET'] = 'GridView1$ctl02$LinkButton1'
        return self.fetch_content(self.query_url, self.post_data)

    def fetch_corp_key(self, code):
        content = self.fetch_query_content(code)
        if content.find(self.search_string) < 0:
            return None
        content = self.fetch_key_content()
        search_obj = self.key_reg.search(content)
        return search_obj and search_obj.groups()[0]

    def fetch_corp_info(self, code):
        print('###############################################################')
        print(self._msg('注册码: %s' % code))
        corp_key = self.fetch_corp_key(code)
        if corp_key == None:
            print('没找到相关信息.')
            return []
        print('key: %s' % corp_key)
        url = self.corp_url.format(corp_key)
        content = self.fetch_content(url, update_events=False)
        result = []
        search_obj = self.reg.search(content)
        if search_obj:
            search_obj.groupdict() and result.append(search_obj.groupdict())
            print(search_obj.groupdict())
        if not result:
            logging.info('register code: %s' % code)
        return result

    def save(self, register_code):
        self._save_times = (self._save_times + 1) % 101
        self._save_times or self.model.commit()
        corps = self.fetch_corp_info(register_code)
        if not corps:
            return False
        for corp in corps:
            self.model.add(self._process(corp), is_commit=False)
            print('添加成功!')
        print('###############################################################')
        return True

    def action(self):
        invalid_times = 0
        while self.nature_num<=99:
            if self.save(self.calc_code15(self.org_code, self.nature_num, self.ord_num)):
                invalid_times = 0
            else:
                invalid_times += 1
            self.ord_num += 1
            if invalid_times >= 500:
                invalid_times = 0
                self.ord_num = 0
                if self.nature_num >=40:
                    self.nature_num = 0
                    self.org_code = str(int(self.org_code)+1)
                    if int(self.org_code)>=440200:
                        break
                else:
                    self.nature_num = 40
                logging.info('org_code: %s nature code: %s' % (self.org_code, self.nature_num))
        self.model.commit()

    def action_test(self):
        pass

    def action_new(self, invalid_times=10):
        for query_obj in self.max_code_model.get_all():
            org_code, nature_num, ord_num = query_obj.org_code, query_obj.nature_num, query_obj.ord_num+1
            times = 0
            while times<invalid_times:
                if self.save(self.calc_code15(org_code, nature_num, ord_num)):
                    times = 0
                    query_obj.ord_num = ord_num
                    # 预防 query_obj.ord_num = ord_num 发生特殊的未commit事件.
                    self._save_times or self.model.commit()
                else:
                    times += 1
                ord_num += 1
            self.model.commit()

    def action_from_invalid_codes(self):
        for query_obj in self.invalid_code_model.get_all():
            if self.save(query_obj.register_code):
                query_obj.delete()
        self.model.commit()

    def action_from_file(self):
        f = open('others.txt')
        for line in f:
            code = line[:-1]
            self.save(code)
        f.close()
        self.model.commit()

    def report(self):
        corps = self.model.filter_by(status='登记成立', insert_date=datetime.date.today())
        #corps = self.model.filter_by(status='登记成立', insert_date=datetime.date(2011,12,8))
        rows = []
        fields = (
            ('名称', 'name'),
            ('注册码', 'register_code'),
            ('地址', 'addr'),
            ('经营范围', 'scope'),
            ('注册资金', 'capital'),
            ('成立日期', 'establishment_data'),
            ('企业性质', 'nature'),
            ('法人', 'representative'),
            ('企业状态', 'status'),
            ('期限', 'period'),
            ('登记单位', 'register_department'),
            ('信息来源', 'info_from'),
            ('更新日期', 'insert_date'),
        )
        self.model.report('广州红盾网最新注册公司信息_%s.csv' % time.strftime('%Y-%m-%d'), fields=fields, rows=corps, encoder='gbk')

if __name__ == '__main__':
    register_corp = Register_corp()
    actions = ({
            'title': '普通抓取',
            'method': register_corp.action
        },{
            'title': '抓取最新',
            'method': register_corp.action_new
        },{
            'title': '从others.txt文件抓取',
            'method': register_corp.action_from_file
        },{
            'title': '从无效的注册码抓取',
            'method': register_corp.action_from_invalid_codes
        },{
            #'title': '初始化无效的注册码',
            #'method': register_corp.init_invalid_codes
        #},{
            'title': '生成报告',
            'method': register_corp.report
        },{
            'title': '退出',
            'method': sys.exit
        }
    )
    for i in range(0, len(actions)):
        print('%s. %s' % (i+1, actions[i]['title']))
    action = input('请选择操作: ')
    actions[int(action.strip())-1]['method']()
