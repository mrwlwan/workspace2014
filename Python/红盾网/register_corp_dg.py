# coding=utf8

from opener import Opener
from lib.models_dg import CorpModel, InvalidCodeModel, MaxCodeModel
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
        self.charset = 'gbk'
        self.opener = Opener(encoding=self.charset)
        # 6位机关代码; 6位
        self.org_code = '441900'
        # 企业性质号码; 2位, 00~30为内资;40~50为外资.
        self.nature_num = 0
        # 流水号; 4位
        self.ord_num= 1
        self.corp_url = 'http://wsnj.gdgs.gov.cn/aiccps/SearchServlet?service=getEntityInfoByPage&registerNo=%s'
        self.search_text_reg = re.compile(r'^<table width="100%" border="0"><tr><td align=center height=200 >找不到相关的数据\.\.</td></tr></table>$')
        self.regs = [
            re.compile(r'<td align=left width=100% colspan=6 height=25>(?P<name>[^<]+)', re.S),
            re.compile(r'址：</td><td align=left valign=top colspan=5>(?P<addr>[^<]*)', re.S),
            re.compile(r'号：</td><td align=left valign=top><font color="red">(?P<register_code>[^<]*)', re.S),
            re.compile(r'[名人]：</td><td align=left valign=top colspan=3>(?P<representative>[^<]*)', re.S),
            re.compile(r'型：</td><td align=left valign=top>(?P<nature>[^<]*)', re.S),
            re.compile(r'限：</td><td align=left valign=top colspan=3>(?P<period>[^<]*)', re.S),
            re.compile(r'本：</td><td align=left valign=top>(?P<capital>[^<]*)', re.S),
            re.compile(r'关：</td><td align=left valign=top colspan=3>(?P<register_department>[^<]*)', re.S),
            re.compile(r'态：</td><td align=left valign=top>(?P<status>[^<]*)', re.S),
            re.compile(r'期：</td><td align=left valign=top colspan=3>(?P<establishment_data>[^<]+)', re.S),
            re.compile(r'围：</td><td align=left valign=top colspan=5>(?P<scope>[^<]*)', re.S),
        ]
        self._save_times = 0
        self._today = get_cst()

    def _msg(self, text):
        return '%s %s' % (time.asctime(), text)

    def _process(self, corp_dict):
        corp_dict['insert_date'] = self._today
        corp_dict['info_from'] = self.info_from
        if 'establishment_data' in corp_dict and corp_dict['establishment_data']:
            corp_dict['establishment_data'] = self.model._str2date(corp_dict['establishment_data'])
        return corp_dict

    def calc_code15(self, org_code, nature_num, ord_num):
        """ 计算15位注册号的检验码. 并返回15位注册号. """
        code14 = '%s%02d%06d' % (org_code, nature_num, ord_num)
        temp =  reduce(lambda x,y: ((x+int(y))%10 or 10)*2%11, code14, 10)
        return '%s%s' % (code14, (11-temp)%10)

    def calc_code13(self, org_code, nature_num, ord_num):
        """ 返回13位注册号. """
        return '%s%s%04d' % (org_code, nature_num, ord_num)

    def init_invalid_codes(self):
        i = 0
        for query_obj in self.max_code_model.get_all():
            org_code, nature_num, max_ord_num = query_obj.org_code, query_obj.nature_num, query_obj.ord_num
            for ord_num in range(0, max_ord_num):
                register_code = self.calc_code15(org_code, nature_num, ord_num)
                if self.model.exists_by(register_code=register_code):
                    continue
                self.invalid_code_model.add({'register_code': register_code}, is_commit=False)
                i += 1
                if not i%200:
                    self.model.commit()
                    print('Save 200 invalid codes!')
        self.model.commit()

    def fetch(self, code):
        print('###############################################################')
        print(self._msg('注册码: %s' % code))
        url = self.corp_url % code
        content = self.opener.urlopen(url, timeout=10, times=0)
        #if content.find(self.search_text) < 0:
        if self.search_text_reg.match(content):
            print('没找到相关信息.')
            return []
        result = []
        temp = {}
        for search_obj in (reg.search(content) for reg in self.regs):
            if search_obj:
                temp.update(search_obj.groupdict())
        print(temp)
        result.append(temp)
        if not result:
            logging.info('register code: %s' % code)
        return result

    def save(self, register_code):
        self._save_times = (self._save_times + 1) % 101
        self._save_times or self.model.commit()
        corps = self.fetch(register_code)
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

    def action_new(self, invalid_times=20):
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
        #corps = self.model.filter_by(status='登记成立', insert_date=datetime.date(2011,11,3))
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
        self.model.report('东莞红盾网最新注册公司信息_%s.csv' % time.strftime('%Y-%m-%d'), fields=fields, rows=corps, encoder='gbk')

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
            'title': '初始化无效的注册码',
            'method': register_corp.init_invalid_codes
        },{
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
