#!/bin/python
#coding=utf-8

import filecmp, shutil, os, sys

SRC = r'Z:/'
DEST = r'M:/'

IGNORE = ['Thumbs.db']

def get_cmp_paths(dir_cmp, filenames):
    return ((os.path.join(dir_cmp.left, f), os.path.join(dir_cmp.right, f)) for f in filenames)

def sync(dir_cmp):
    print(dir_cmp.left)
    for f_left, f_right in get_cmp_paths(dir_cmp, dir_cmp.right_only):
        if os.path.isfile(f_right):
            os.remove(f_right)
        else:
            shutil.rmtree(f_right)
        print('删除 %s' % f_right)
    for f_left, f_right in get_cmp_paths(dir_cmp, dir_cmp.left_only+dir_cmp.diff_files):
        if os.path.isfile(f_left):
            shutil.copy2(f_left, f_right)
        else:
            shutil.copytree(f_left, f_right)
        print('复制 %s' % f_left)
    for sub_cmp_dir in dir_cmp.subdirs.values():
        sync(sub_cmp_dir)

def sync_files(src, dest, ignore=IGNORE):
    if os.path.isfile(src) or os.path.isfile(dest):
        print('只能对文件夹进行同步, 请正确输入源文件夹和目标文件夹...')
        return
    dir_cmp = filecmp.dircmp(src, dest, ignore=['Thumbs.db'])
    sync(dir_cmp)
    print('同步完成!')

if __name__ == '__main__':
    src, dest = SRC, DEST
    if len(sys.argv) == 3:
        src, dest = sys.argv[1:3]
    sync_files(src, dest)
    input()
