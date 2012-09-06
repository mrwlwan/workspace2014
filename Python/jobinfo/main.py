# coding=utf8

from lib.job5156_corp import Job5156Corp
from lib.jobcn_corp import JobcnCorp
from lib.job51_corp import Job51Corp
from lib.job58_corp import Job58Corp
from lib.job577_corp import Job577Corp
from lib.jobcfw_corp import JobcfwCorp
from lib.jobinj_corp import JobINJCorp
from lib.zjrc_corp import ZJRCCorp
from lib.job168_corp import Job168Corp
from lib.jobefhr_corp import JobefhrCorp
from lib.tzrc_corp import TZRCCorp
from lib.qlrc_corp import QLRCCorp
from lib.zjrc_corp2 import ZJRCCorp as ZJRCCorp2
from lib.job168_corp2 import Job168Corp as Job168Corp2
from funcs import shortcut_input
import sys

CORPCLASSES = (
    {'title': 'Job5156', 'class': Job5156Corp},
    {'title': '51Job', 'class': Job51Corp},
    {'title': 'Jobcn', 'class': JobcnCorp},
    #{'title': '58同城', 'class': Job58Corp},
    {'title': '瑞安人才网', 'class': Job577Corp},
    #{'title': '中国服装人才网', 'class': JobcfwCorp},
    {'title': '中国注塑人才网', 'class': JobINJCorp},
    #{'title': '浙江人才网', 'class': ZJRCCorp},
    {'title': '南方人才网', 'class': Job168Corp},
    {'title': '台州人才网', 'class': TZRCCorp},
    {'title': '齐鲁人才网', 'class': QLRCCorp},
    #{'title': '服装人才网', 'class': JobefhrCorp},
    #{'title': '浙江人才网2', 'class': ZJRCCorp2},
    #{'title': '南方人才网2', 'class': Job168Corp2},
)

OPERATIONS = (
    {'title': '抓取信息', 'method': 'action'},
    {'title': '生成报告', 'method': 'report'},
)

CACHES = {}

if __name__ == '__main__':
    while 1:
        class_index = shortcut_input(CORPCLASSES, title='title', input_msg='请选择目标: ')
        if class_index < 0:
            sys.exit()
        title = CORPCLASSES[class_index]['title']
        title in CACHES or CACHES.update({title: CORPCLASSES[class_index]['class']()})
        corp = CACHES[title]
        method_index = shortcut_input(OPERATIONS, title='title', input_msg='请选择操作: ')
        if method_index < 0:
            continue
        getattr(corp, OPERATIONS[method_index]['method'])()
        del CACHES[title]

