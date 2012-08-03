#!bin/pyhton3
# coding=utf8

import funcs
import os, sys, getopt, functools
from PIL import Image

# 源图片路径
SRC = os.getcwd()
# 目标保存图片的路径
DEST = os.getcwd()
# 缩略图保存的文件夹名称, 最终缩略图的保存路径为 sys.path.join(DEST, THUMB_DIR).
THUMB_DIR = '缩略图'
# 缩放比例
RATE = 0.15
# 指定高
FIXED_HIGHT = [140, 65]
# 缩略图的命名, 在原文件名前加上 THUMB_PREFFIX, 如"thumb_"
THUMB_PREFFIX = ''
# 是否递归搜索子文件夹
IS_RECURSIVE = True

def coroutine(func):
    """ 用于协程的装饰器 """
    @functools.wraps('func')
    def start(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return start

@coroutine
def thumb(save_path, rate=1, fixed_hight=None, thumb_preffix=''):
    img_exts = ('.jpg', '.jepg', '.gif', '.png', '.bmp')
    saved_filenames = set()
    repeatd_times = 0
    while 1:
        img_path = (yield)
        img_ext = os.path.splitext(img_path)[1].lower()
        if not img_ext in img_exts:
            continue
        print(img_path)
        save_filename = '%s%s%s' % (thumb_preffix, os.path.splitext(os.path.split(img_path)[1])[0], img_ext)
        if save_filename in saved_filenames:
            repeatd_times += 1
            save_filename = '%s_%s%s' % (os.path.splitext(save_filename)[0], repeatd_times, img_ext)
        img = Image.open(img_path)
        rate = rate if not fixed_hight else fixed_hight>=img.size[1] and 1 or fixed_hight/img.size[1]
        img.thumbnail((int(img.size[0]*rate), int(img.size[1]*rate)), 1)
        img.save(os.path.join(save_path, save_filename))
        saved_filenames.add(save_filename)
        print('%s %s' % ('Thumb', save_filename))

def process(src, func, is_recursive=True):
    files = []
    dirs = []
    for f in os.listdir(src):
        path = os.path.join(src, f)
        if os.path.isfile(path):
            files.append(path)
        elif is_recursive and os.path.isdir(path) and f.lower() not in ('缩略图', 'thumb', 'thumbs', 'thumbnail', 'thumbnails'):
            dirs.append(path)
    for path in files:
        func.send(path)
    for path in dirs:
        process(path, func, is_recursive)

if __name__ == '__main__':
    src, dest, thumb_dir, rate, thumb_preffix, is_recursive = SRC, DEST, THUMB_DIR, RATE, THUMB_PREFFIX, IS_RECURSIVE
    opts, args = getopt.getopt(sys.argv[1:], 'r:d:p:s')
    print(opts, args)
    for k,v in opts:
        if k == '-r':
            rate = float(v)
        elif k == '-d':
            thumb_dir = v
        elif k == '-p':
            thumb_preffix = v
        elif k == '-s':
            is_recursive = False
    if args:
        args.append(os.getcwd())
        src, dest = args[:2]

    print(src, dest, thumb_dir, rate, thumb_preffix, is_recursive)
    save_path = os.path.join(dest, thumb_dir)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    index = funcs.shortcut_input([{'title': item} for item in FIXED_HIGHT])
    fixed_hight = FIXED_HIGHT[index]
    my_thumb = thumb(save_path, rate, fixed_hight=fixed_hight, thumb_preffix=thumb_preffix)
    process(src, my_thumb, is_recursive)
    print('\nDone!')
    input()
