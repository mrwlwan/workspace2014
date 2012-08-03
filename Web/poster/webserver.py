#!bin/python3
# coding=utf8

from lib.bottle import run, view, template, request, response, route, post, get, static_file, TEMPLATE_PATH, debug
from lib import mylib, config
from poster import Poster
#################################################
debug(True)
TEMPLATE_PATH.append('./template')
exception_format = ' <span style="color: red">%s :(</span>'
config = config.Config('config.cfg')
# 格式: posters = {username: Poster}
#test_poster = Poster(
    #{'username': 'justforfun', 'password': '123456'},
    #config.get_section('global')['global'],
    #config.get_section('user_section1')['user_section1']
#)
#posters = {'test': test_poster}
posters = {}
auths = {}
is_action = False
#################################################
def get_form_dict(form, is_user_section=False):
    """ is_user_seciton 参数, 是为了处理 checkbox 和 radiobox 不选中时不传值过来的情况 """
    temp = {}
    if is_user_section:
        temp = {
            'is_random': '0',
            'is_repeat': '0'
        }
    for key in form:
        temp[key] = form.getone(key)
    return temp

def update_auths_posters():
    auths.clear()
    sections = config.get_sections()
    global_config = sections['global']
    user_sections = sections['user_sections']
    for section_name in user_sections:
        auth_stings = user_sections[section_name].pop('auths')
        for auth_string in (auth_string for auth_string in auth_stings.split(' ') if auth_string.strip()):
            username, password = auth_string.split(':', 1)
            auths[username] = {
                'username': username.strip(),
                'password': password.strip()
            }
            if username in posters:
                posters[username].set_person_config(user_sections[section_name])
            else:
                posters[username] = Poster(auths[username], global_config, user_sections[section_name], False, False)

#################################################
@route('/:path#(css|script).+#')
def server_static(path):
    """ 处理 static files. """
    return static_file(path, root='')

@route('/')
@view('index.tpl')
def index_tpl():
    """ 首页. """
    global is_action
    config.init()
    c = config.get_sections()
    global_configs = c['global']
    user_sections = c['user_sections']
    return {
        'global_configs': global_configs,
        'user_sections': user_sections,
        'is_action': is_action
    }

@post('/section/:section_name')
def update_section(section_name):
    is_user_section = config.is_user_section(section_name)
    apply_name = request.forms.get('apply')
    try:
        if apply_name == 'submit':
            form = get_form_dict(request.forms, is_user_section)
            config.update({
                section_name: form
            }, save=True)
            return '保存成功 :)'
        if apply_name == 'delete':
            config.delete(section_name)
            return '删除成功 :)'
    except Exception as e:
        return exception_format % e

@post('/add/user_section')
@view('section_form.tpl')
def add_user_section():
    """ 返回一个空的 User Section. """
    user_section = config.get_empty_section('user_section')
    section_name, section_config = user_section.popitem()
    section_config.update({
        'section_name': section_name
    })
    return section_config

@post('/login_forms')
@view('auth_login_forms.tpl')
def get_auth_login_forms():
    global is_action
    if not is_action:
        update_auths_posters()
    return {
        'auth_login_forms': auths.values(),
        'global_config': config.get_section('global')['global'],
        'posters': posters,
        'is_action': is_action
    }

@get('/login_code/:username')
def get_login_code(username):
    """ 返回验证码. """
    img = None
    if username in posters:
        poster = posters[username]
        img = poster.get_login_code()
    response.content_type = 'image/BMP'
    return img

@post('/auth_login/:username')
def login(username):
    poster = posters[username]
    post_data = get_form_dict(request.forms)
    if poster.is_logined():
        return '帐户已登录'
    if poster.login(post_data):
        return '登录成功'
    return exception_format % '登录失败, 请检查账户信息是否正确'

@post('/action')
def action():
    global is_action
    if is_action:
        is_action = False
        Poster.pause()
        print('停止灌水')
        return exception_format % '停止灌水'
    action_posters = [posters[username] for username in auths if posters[username].is_logined()]
    Poster.set_action(True)
    for poster in action_posters:
        poster.prepare()
    for poster in action_posters:
        try:
            poster.start()
        except Exception as e:
            print(e)
            print('继续灌水')
            poster.resume()
    is_action = True
    return '开始灌水'


run(host='localhost', port=8080, reloader=True)
