#!/usr/bin/python3
# coding=utf8

import subprocess, sys, time, os

def popen(command, cwd=None, input_bytes=b'', is_wait=True):
    p = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=sys.stdout)
    input_bytes and p.communicate(input_bytes)
    is_wait and p.wait()

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    commands = [
        {'command': 'hg pull -u'},
        {'command': 'hg pull -u'},
        {'command': 'python3 main.py', 'cwd': 'jobinfo', 'input_bytes': b'1\n1\n0\n'},
        {'command': 'hg comm -m "daily update."'},
        {'command': 'hg push'},
        {'command': 'hg push'},
    ]
    for command in commands:
        popen(**command)
        print("Next command..")
