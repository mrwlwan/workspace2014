#!bin/python3
# coding=utf8

import re, zipfile, os, sys

maxversion = 100
ff_maxversion_reg = re.compile(br'(ec8030f7-c20a-464f-9b0e-13a3a9e97384.*?em:maxVersion.*?)([^>< ="/]+)', re.S+re.I)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        maxversion = int(sys.argv[1])
    print('Target Maxversion: %s\n' % maxversion)

    for filename in os.listdir():
        print('%s ' % filename, end='')
        if os.path.isdir(filename) or not filename.lower().endswith('.xpi'):
            print('skip.')
            continue
        zin = zipfile.ZipFile(filename)
        rdf = zin.read('install.rdf')
        version = 0
        for item in ff_maxversion_reg.finditer(rdf):
            match_obj = re.search(br'\d+', item.groups()[1])
            if match_obj and int(match_obj.group()) > version:
                version = int(match_obj.group())
        if version >= maxversion:
            zin.close()
            print('skip.')
            continue

        zout = zipfile.ZipFile('new.xpi','w')
        rdf = ff_maxversion_reg.sub(br'\g<1>'+ str(maxversion).encode('utf8'), rdf)
        zout.writestr('install.rdf', rdf)
        for item in zin.infolist():
            if item.filename.lower() == 'install.rdf':
                continue
            else:
                buffer = zin.read(item.filename)
                zout.writestr(item, buffer)
        zin.close()
        zout.close()
        os.remove(filename)
        os.rename('new.xpi', filename)
        print('done!')


