# coding=utf8

from lib.corp import Commiter, Corp
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
from lib.jobxmrc_corp import JobXmrcCorp
from lib.zjrc_corp2 import ZJRCCorp as ZJRCCorp2
from lib.job168_corp2 import Job168Corp as Job168Corp2
from funcs import shortcut_input
import sys, multiprocessing, time

CORPCLASSES = (
    {'title': 'Job5156', 'class': Job5156Corp},
    {'title': '51Job', 'class': Job51Corp},
    {'title': 'Jobcn', 'class': JobcnCorp},
    {'title': '南方人才网', 'class': Job168Corp},
    {'title': '厦门人才网', 'class': JobXmrcCorp},
    #{'title': '58同城', 'class': Job58Corp},
    #{'title': '中国服装人才网', 'class': JobcfwCorp},
    #{'title': '浙江人才网', 'class': ZJRCCorp},
    {'title': '台州人才网', 'class': TZRCCorp},
    {'title': '瑞安人才网', 'class': Job577Corp},
    {'title': '齐鲁人才网', 'class': QLRCCorp},
    {'title': '中国注塑人才网', 'class': JobINJCorp},
    #{'title': '服装人才网', 'class': JobefhrCorp},
    #{'title': '浙江人才网2', 'class': ZJRCCorp2},
    #{'title': '南方人才网2', 'class': Job168Corp2},
)

OPERATIONS = (
    {'title': '抓取信息', 'method': 'start'},
    {'title': '生成报告', 'method': 'report'},
)


if __name__ == '__main__':
    while 1:
        method_index = shortcut_input(OPERATIONS, title='title', input_msg='请选择操作: ')
        if method_index < 0:
            continue
        method = OPERATIONS[method_index]['method']
        class_indexes = shortcut_input(CORPCLASSES, title='title', input_msg='请选择目标: ', multi=True)
        if len(class_indexes) <= 0:
            sys.exit()
        queue = multiprocessing.Queue()
        processes = []
        for class_index in class_indexes:
            title = CORPCLASSES[class_index]['title']
            corp = CORPCLASSES[class_index]['class']()
            processes.append(corp)
            corp.set_queue(queue)
            getattr(corp, method)()
        if method == 'start':
            commiter = Commiter(queue=queue, db_lock=None, process_num=len(processes))
            commiter.start()
            commiter.join()
            for process in processes:
                process.join()
