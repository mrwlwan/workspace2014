#!usr/bin/python3
# coding=utf8

from bottle import run, view, template, request, response, route, post, get, static_file, TEMPLATE_PATH, debug
from lib.web_poster import Web_poster
from lib.config import Config
import re, functools, time, json

TEMPLATE_PATH.append('./template')
#debug(True)

poster = Web_poster()
config = Config('config.cfg')

####################################################
def _msg(msg=''):
    return '[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg)

def _dict(form):
    d = {}
    for key in form:
        d[key] = str(form.get(key)).strip()
    return d

def _dict2str(d):
    return '\n'.join(map(lambda x: '%s: %s' % x, sorted(d.items(), key=lambda x:x[0])))

def _update_general(form):
    """ 更新 web_poster 对象的属性. 参数 form 可以是 request.forms, 也可以是 dict. """
    for prop in ('charset', 'headers'):
        if prop not in form:
            continue
        value = form.get(prop).strip()
        if value and hasattr(poster, prop):
            if prop in ['headers']:
                value = json.loads(value)
            setattr(poster, prop, value)

####################################################
@route('/lib/:path#(js|css).+#')
def server_lib_static(path):
    """ 处理库js,css等static files. """
    return static_file(path, root='../../../lib')

@route('/:path#(script|css).+#')
def server_user_static(path):
    """ 处理用户js,css等static files. """
    return static_file(path, root='')

@route('/block/:block_name')
def get_block(block_name):
    """ block 模块载入. """
    return template('block/%s.tpl' % block_name)

@route('/index')
@route('/')
def index():
    """ 首页 """
    return static_file('index.html', root='')

@post('/general/update')
def update_general():
    """ 更新 web_poster 对象的属性. """
    try:
        _update_general(request.forms)
        return _msg('更新成功')
    except Exception as e:
        print(e)
        return _msg('更新失败')

@post('/cookie/clear')
def clear_cookie():
    poster.logout()
    return _msg('清除cookie成功')

@post('/re_test')
def re_test():
    """ 正则测试. """
    try:
        text = request.forms.get('re_test_text', None)
        flags = functools.reduce(lambda x,y: x | int(y), request.forms.getall('flags'), 0)
        reg = re.compile(request.forms.get('reg'), flags)
        lines = [_msg('Text: "%s", Reg: "%s", Flags: %s' % (text if text is not None else '<网页抓取的内容>', reg.pattern, flags))]
        search_objs = poster.re_test(reg, text)
        if not search_objs:
            lines.append('没找到匹配\n')
        for search_obj in search_objs:
            lines.append("Group: %s\nGroups: %s\nGroup dict: %s\n" % (search_obj.group(), search_obj.groups(), search_obj.groupdict()))
        return '\n'.join(lines)
    except Exception as e:
        return str(e)

@post('/search')
def search():
    """ 搜索功能. """
    try:
        text = request.forms.get('search_text', None)
        target = request.forms.get('search_target')
        is_case = bool(int(request.forms.get('search_is_case', '0')))
        start_pos = request.forms.get('search_start_pos').strip()
        start_pos = int(start_pos) if start_pos is not '' else None
        end_pos = request.forms.get('search_end_pos').strip()
        end_pos = int(end_pos) if end_pos is not '' else None

        lines = [_msg('Text: "%s", Target: "%s", Start: %s, End: %s, Case Sensitive: %s' % (text if text is not None else '<网页抓取的内容>', target, start_pos, end_pos, is_case))]
        search_flag = poster.search(target, text, start_pos, end_pos, is_case)
        text_length = len(text if text is not None else poster.get_content())
        start_pos = start_pos if start_pos is not None else 0
        end_pos = end_pos if end_pos is not None else text_length
        lines.append("目标位置: %s\n搜索长度: %s\n文本长度: %s\n" % (search_flag, end_pos-start_pos, text_length))
        return '\n'.join(lines)
    except Exception as e:
        print(e)
        return str(e)

@post('/fetch/content')
def fetch():
    """ 抓取网页. """
    msg = '%s'
    try:
        poster.update_config(_dict(request.forms))
        flag =  poster.fetch_content()
        msg = _dict2str(poster.get_request_info()) + '\n结果: %s\n'
        if flag:
            #print(poster.get_content())
            return _msg(msg % '抓取成功')
        return _msg(msg % '抓取失败')
    except Exception as e:
        print(e)
        return _msg(msg % '抓取失败')

@post('/show/content')
#@view('content.tpl')
def get_content():
    """ 显示抓取到的网页内容. """
    #is_raw = bool(request.query.get('raw', ''))
    #return dict(content=poster.get_content(is_raw))
    try:
        return _msg(poster.get_content(False))
    except Exception as e:
        print(e)
        return '没抓取到内容'

@post('/show/response_info')
def get_response_info():
    """ 显示response headers. """
    try:
        return _msg(_dict2str(poster.get_response_info()))
    except Exception as e:
        print(e)
        return '无效Response Info.'

@post('/show/request_info')
def get_request_info():
    """ 显示request headers. """
    try:
        return _msg(_dict2str(poster.get_request_info()))
    except Exception as e:
        print(e)
        return '无效Request Info.'

@post('/show/request_headers')
def get_request_headers():
    """ 显示Request Headers. """
    try:
        return _msg(_dict2str(poster.headers))
    except Exception as e:
        print(e)
        return '无效Request Headers.'

@get('/get_code_image')
def get_code():
    """ 显示验证码图片. """
    url = request.query.get('url').strip()
    response.content_type = 'image/BMP'
    return poster.get_code_img(url)

@get('/session/json')
def get_session_json():
    return {
      'identifier': "name",
      'label': "name",
      'items': [{'name': section_name} for section_name in sorted(config.get_section_names())]
    }

@post('/session/save')
def save_session():
    """ 保存会话. """
    try:
        section_config = _dict(request.forms)
        section_name = section_config.pop('session_name')
        config.update({
            section_name: section_config
        }, is_save=True)
        return '保存 Session: %s 成功!' % section_name
    except Exception as e:
        print(e)
        return '保存 Session: %s 失败!' % section_name

@post('/session/remove')
def remove_session():
    """ 删除会话. """
    try:
        section_name = request.forms.get('session_name').strip()
        if section_name not in config.get_section_names():
            return '无效的 Session 名称: %s.' % section_name
        config.remove(section_name, is_save=True)
        return '删除 Session: %s 成功!' % section_name
    except Exception as e:
        print(e)
        return '删除 Session: %s 失败' % section_name

@post('/session/clear')
def clear_session():
    """ 清空所有会话. """
    try:
        config.clear(is_save=True)
        return '清空 Sessions 成功!'
    except Exception as e:
        print(e)
        return '清空 Sessions 失败!'

@post('/session/load')
def load_session():
    """ 加载会话. """
    try:
        section_name = request.forms.get('session_name').strip()
        if section_name not in config.get_section_names():
            return '无效的 Session 名称: %s.' % section_name
        section_config = config.get_section_config(section_name)
        _update_general(section_config)
        return section_config
    except Exception as e:
        print(e)
        return '加载 Session: %s 失败' % section_name

@post('/save_log')
def save_log():
    print(request.forms.dict)
    try:
        f = open('log.txt', 'w')
        f.write(request.forms.get('content').strip())
        f.close()
        return '保存 log 成功!'
    except Exception as e:
        print(e)
        return '保存 log 失败!'

run(host='localhost', port=8080, reloader=True)
