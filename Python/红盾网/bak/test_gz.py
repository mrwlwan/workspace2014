# coding=utf8

from lib.opener import Opener
import re, sys

if __name__ == '__main__':
    base_url = 'http://wap.gzaic.gov.cn/Entity/Default.aspx?__ufps={0}'
    corp_url = 'http://wap.gzaic.gov.cn/Entity/show.aspx?id={0}'
    ufps = ''
    data = {
        'btnSearchQy': '查询企业基本信息',
        'txtEntName': '',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': ''
    }
    opener = Opener(has_cookie=True)
    html = opener.open(base_url, raw_string=False)
    print('************************************************')
    ufps_reg = re.compile(r'__ufps=(?P<__ufps>\d*)')
    search_obj = ufps_reg.search(html)
    if search_obj:
        ufps = search_obj.groups()[0]
        print('__ufps: %s' % ufps)
    else:
        print('__ufps not found!')
        sys.exit()
    register_code = '4401011103185'
    data['txtRegNO'] = register_code
    url = base_url.format(ufps)
    print('************************************************')
    html = opener.open(url, data, raw_string=False)
    print('************************************************')
    ufps = ufps_reg.search(html).groups()[0]
    if html.find('__VIEWSTATE') < 0:
        sys.exit()
    corp_id_reg = re.compile(r'show\.aspx\?id=(?P<id>\d*)"')
    corp_id = ''
    search_obj = corp_id_reg.search(html)
    if search_obj:
        corp_id = search_obj.groups()[0]
        print('corp id: %s' % corp_id)
    else:
        print('Not found corp id!')
        sys.exit()
    url = corp_url.format(corp_id)
    html = opener.open(url, raw_string=False)
    print('************************************************')
    corp_info = {
        'register_code': register_code,
        'status': '登记成立',
        'period': '长期',
    }

    corp_reg = re.compile(r'注册号：(?P<register_code>[^<]*)<br>[^：]*企业名称：(?P<name>[^<]*)<br>[^：]*企业地址：(?P<addr>[^<]*)<br>[^：]*企业状态：[^\n]*<br>[^：]*负责人：(?P<representative>[^<]*)<br>[^：]*企业类型：(?P<nature>[^<]*)<br>[^：]*成立日期：(?P<establishment_data>[^<]*)<br>[^：]*核准日期：[^\n]*<br>[^：]*注册资本：(?P<capital>[^<]*)<br>[^：]*实收资本：[^\n]*<br>[^：]*登记机关：(?P<register_department>[^<]*)<br>[^：]*经营范围：(?P<scope>[^<]*)<br>', re.S)
    search_obj = corp_reg.search(html)
    if search_obj:
        corp_info.update(search_obj.groupdict())
        print(corp_info)
    else:
        print('Not match!')
    corp_id = search_obj.groups()[0]

