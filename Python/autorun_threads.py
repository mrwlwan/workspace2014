#!/usr/bin/python3
# coding=utf8

import subprocess, sys, threading, time, os

def popen(command, cwd=None, input_bytes=b'', is_wait=True):
    p = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=sys.stdout)
    input_bytes and p.communicate(input_bytes)
    is_wait and p.wait()

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    popen('hg pull -u')
    popen('hg pull -u')
    commands = [
        {'command': 'python3 main.py', 'cwd': 'jobinfo', 'input_bytes': b'1\n1\n2\n1\n3\n1\n0\n'},
        {'command': 'python3 register_corp_dg.py', 'cwd': '红盾网', 'input_bytes': b'2\n'},
        {'command': 'python3 register_corp_gz.py', 'cwd': '红盾网', 'input_bytes': b'2\n'},
    ]
    threads = [threading.Thread(target=popen, kwargs=command) for command in commands]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    popen('hg comm -m "daily update."')
    popen('hg push')
    popen('hg push')
