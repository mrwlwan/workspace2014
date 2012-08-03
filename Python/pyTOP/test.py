#!bin/python3
# coding=utf8

import pytop.topapi as api
import pytop.topclient as client
import xml.etree.ElementTree as etree

if __name__ == '__main__':
    app_key = '12307923'
    app_secret = 'f03ec38fa4f3cfb1ab198ca90838d40a'
    c = client.TOPClient(app_key, app_secret)
    r = api.UserGetRequest(fields='user_id,uid,nick,sex,saadsfsdf', nick='有娴自远方来', test=123)
    rs = c.get(r, is_transform=True, session='6101823005b2bc348fae5f3d71da19813fb6b5d9467e86976566553')
    print(rs.response)

    c2 = client.TOPAuthClient(app_key, app_secret, redirect_uri='http://127.0.0.1')
    token_obj = c2.fetch_token('server', 'F29ZQxF2SCVXYa4UPoYtyWb16461', state='1212')
    print(token_obj)

