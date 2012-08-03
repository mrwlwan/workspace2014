#!/bin/python
#coding=utf-8

import filecmp, shutil, os, sys

SRC = ur'Z:/'
DEST = ur'M:/2010'

#def log(logfile, message, filepath):
#    print message,'\n',filepath
#    logfile.write(message+'\n'+filepath+'\n')

def syncFiles(src, dest):
    walk(src, dest)

def walk(src, dest):
    print '****************************************************************'
    print dest
    print '****************************************************************'
    dirCmp = filecmp.dircmp(src, dest, ignore=['Thumbs.db'])
    for destFile in dirCmp.right_only:
        destFilePath = dest+'/'+destFile
        if os.path.isfile(destFilePath):
            print u'删除文件\n',destFilePath
            os.remove(destFilePath)
        else:
            print u'删除文件夹\n',destFilePath
#            os.rmdir(destFilePath)
            shutil.rmtree(destFilePath)
    for srcFile in dirCmp.left_only:
        srcFilePath = src+'/'+srcFile
        destFilePath = dest+'/'+srcFile
        if os.path.isfile(srcFilePath):
            print u'复制文件\n',destFilePath
            shutil.copy2(srcFilePath, dest)
        else:
            print u'复制文件夹\n',destFilePath
            shutil.copytree(srcFilePath, destFilePath)
    for srcFile in dirCmp.diff_files:
        srcFilePath = src+'/'+srcFile
        destFilePath = dest+'/'+srcFile
        print u'同步文件\n',destFilePath
        shutil.copy2(srcFilePath, dest)
    subDirs = set(os.listdir(src))-set(dirCmp.left_only)
    targetDirs = [subDir for subDir in subDirs if os.path.isdir(src+'/'+subDir)]
    for targetDir in targetDirs:
        walk(src+'/'+targetDir, dest+'/'+targetDir)

if __name__ == '__main__':
    if not os.path.exists(SRC):
        print u'同步源不存在', SRC
        sys.exit()
    if not os.path.exists(DEST):
        print u'正在复制文件...'
        shutil.copytree(src,dest)
        print u'同步成功!'
        sys.exit()
    syncFiles(SRC, DEST)
    print '\n',u'同步成功!'
    raw_input()
