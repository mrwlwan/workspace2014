#!bin/python
# coding=utf8

import json, urllib2, re, datetime

def urlopen(url, data=None, timeout=None):
    while 1:
        try:
            html = urllib2.urlopen(url, data, timeout)
            if html.getcode() == 200:
                return html.read()
        except Exception as e:
            print 'urllib2.urlopen Error!'

def money(url):
    html = urlopen(url)
    json_str = re.sub(r'(?<=",)|(?=:)|(?<=\{)', r'"', html)
    print json_str
    return json.loads(json_str.decode('gbk'))

def _format_string(objs, keys, ratio):
    for obj in objs:
        for key in keys:
            obj[key] = str(float(obj[key])*ratio)

def _format_float(objs, keys):
    for obj in objs:
        for key in keys:
            obj[key] = '%.2f' % float(obj[key])

def _format(objs):
    _format_string(objs, ('turnover', 'amount', 'inamount', 'outamount', 'netamount'), 0.0001)
    _format_float(objs, ('amount', 'inamount', 'outamount', 'netamount', 'r0x_ratio'))


# 交集
def net_ratio(json_objs1, json_objs2):
    temp_dict = {}
    for json_obj in json_objs1+json_objs2:
        if json_obj['symbol'] not in temp_dict:
            temp_dict[json_obj['symbol']] = json_obj
    symbols1 = [json_obj['symbol'] for json_obj in json_objs1]
    symbols2 = [json_obj['symbol'] for json_obj in json_objs2]
    return [temp_dict[symbol] for symbol in set(symbols1) & set(symbols2)]

def create_file(file_name, json_objs):
    f = open(file_name, 'w')
    #all_keys = ('name', 'trade', 'changeratio', 'turnover', 'amount', 'inamount', 'outamount', 'netamount', 'ratioamount', 'r0_in', 'r0_out', 'r0_net', 'r3_in', 'r3_out', 'r3_net', 'r0_ratio', 'r3_ratio', 'r0x_ratio')
    keys = ('name', 'trade', 'changeratio', 'turnover', 'amount', 'inamount', 'outamount', 'netamount', 'ratioamount', 'r0x_ratio')
    file_strings = [u'日期\t市场\t代码\t名称\t最新价\t涨跌幅\t换手率\t成交额\t流入资金\t流出资金\t净流入\t净注入率\t主力罗盘']
    for json_obj in json_objs:
        temp = [datetime.datetime.now().strftime('%Y-%m-%d')]
        temp.append(json_obj['symbol'][:2])
        temp.append(json_obj['symbol'][2:])
        for key in keys:
            temp.append(json_obj[key])
        file_strings.append('\t'.join(temp))
    f.write('\n'.join(file_strings).encode('gbk'))
    f.close()

if __name__ == '__main__':
    net_url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_ssggzj?page=1&num=20&sort=netamount&asc=0&bankuai=&shichang='
    ratio_url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_ssggzj?page=1&num=20&sort=ratioamount&asc=0&bankuai=&shichang='
    json_objs_net = money(net_url)
    _format(json_objs_net)
    create_file('net_%s.txt' % datetime.datetime.now().strftime('%Y%m%d'), json_objs_net)
    json_objs_ratio = money(ratio_url)
    _format(json_objs_ratio)
    create_file('ratio_%s.txt' % datetime.datetime.now().strftime('%Y%m%d'), json_objs_ratio)
    json_objs_net_ratio = net_ratio(json_objs_net, json_objs_ratio)
    create_file('net_ratio_%s.txt' % datetime.datetime.now().strftime('%Y%m%d'), json_objs_net_ratio)

    raw_input(u'Done!')
