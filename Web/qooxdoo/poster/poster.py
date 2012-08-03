#!bin/python3
# coding=utf8

from bottle import route, run, static_file

@route('/source/:path#.+#')
def server_static(path):
    print(path)
    return static_file(path, root='source/')

@route('/fetch_global')
def fetch_global():
    print('fetchabc')
    return {'auths':'abcdefg'}

run(host='localhost', port=8080, reloader=True)
