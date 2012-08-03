# coding=utf8

from mylib import *
import urllib.request
import urllib.parse
import time
import hashlib


#获得当前时间
t = time.localtime()

#参数数组
paramArray = {
	'app_key':'12307923',
    'session':'',
	'method':'taobao.user.get',
	'format':'json',
	'v':'2.0',
	'timestamp':time.strftime('%Y-%m-%d %X', t),
	'fields':'user_id,uid,nick,sex,buyer_credit,seller_credit,location,created,last_visit,birthday,type,status,alipay_no,alipay_account,alipay_account,email,consumer_protection,alipay_bind',
    'sign_method': 'md5',
    'nick':'pytaobao',
    'partner_id':'top-apitools'
}

#签名函数
def _sign(param,sercetCode):
	src = sercetCode + ''.join(["%s%s" % (k, v) for k, v in sorted(param.items())]) + sercetCode
	return hashlib.md5(src.encode('utf8')).hexdigest().upper()


if __name__ == '__main__':
    #生成签名
    sign = _sign(paramArray, '');
    paramArray['sign'] = sign

    #组装参数
    form_data = urllib.parse.urlencode(paramArray).encode('utf8')

    #访问服务
    #opener = Opener(has_cookie=True)
    json = urllib.request.urlopen('http://gw.api.tbsandbox.com/router/rest', form_data)

    rsp = json.read()
    rsp = rsp.decode('UTF-8')
    print(rsp)

