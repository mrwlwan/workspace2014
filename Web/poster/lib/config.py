# coding=utf8

import configparser, re

class Config:
    parser = None
    config_filename = None
    _used_section_nos = set()
    config = {
        'user_section': {
            'auths': {
                'label': '账号',
                'validate': 'auths'
            },
            'target_urls': {
                'label': '目标帖子',
                'validate': 'mutil_not_null'
            },
            'delay': {
                'label': '时间间隔',
                'validate': 'num'
            },
            'is_repeat': {
                'label': '重复',
                'validate': 'bool'
            },
            'is_random': {
                'label': '循环',
                'validate': 'bool'
            },
            'target_filename': {
                'label': '灌水文本',
                'validate': 'not_null'
            }
        },
        'validations': {
            'null': re.compile(''),
            'not_null': re.compile(r'.+?'),
            'auths': re.compile(r'^(?:[^ :]+?:[^ ]+?(?: +|\Z))+$'),
            'mutil_not_null': re.compile(r'^(?:[^ ]+?(?: |\Z))+$'),
            'num': re.compile(r'^\d+$'),
            'bool': re.compile(r'^[01]$')
        }
    }

    @classmethod
    def create_parser(cls, config_filename):
        if cls.parser:
            return
        cls.config_filename = config_filename
        cls.parser = configparser.ConfigParser(allow_no_value=True)
        cls.parser.read(config_filename, encoding='utf8')

    def __init__(self, config_filename=None):
        """ 首次创建实例时必须指定 config_filename, 此 config_filename 为类的 config_filename 的值. 后面再创建的实例时, 即使指定 config_filename 参数, 类的 config_filename 值也不会改变, 只会改变 self.config_filename 的值, self.config_filename 用于 save. """
        config_filename = Config.config_filename and Config.config_filename or config_filename
        self.config_filename = config_filename
        if not config_filename:
            raise Exception('config file 未定义')
        Config.create_parser(config_filename)

    def _add_section_no(self, no):
        Config._used_section_nos.add(no)

    def _delete_section_no(self, no):
        if no in Config._used_section_nos:
            Config._used_section_nos.remove(no)
            return True
        return False

    def init(self):
        """ 当 index 页面刷新时,必须调用 init 方法, 重置 _used_section_nos """
        Config._used_section_nos.clear()

    def is_user_section(self, section_name):
        return section_name.startswith('user_section')

    def get_parser(self):
        return Config.parser

    def get_section_no(self, user_section_name):
        """ 取得 user_section 的 section_no """
        return int(re.search(r'\d+$', user_section_name).group())

    def get_used_section_nos(self):
        if not Config._used_section_nos:
            parser = self.get_parser()
            Config._used_section_nos.update((self.get_section_no(section_name) for section_name in parser.sections() if self.is_user_section(section_name)))
        return Config._used_section_nos

    def get_new_section_no(self):
        """ 取得一个可用的 section_no, 用于新建一个 user_section 时指定期 section_name 和 section_no """
        used_section_nos = self.get_used_section_nos()
        new_section_no = min(set(range(1, max(used_section_nos) + 2)) - used_section_nos)
        self._add_section_no(new_section_no)
        return new_section_no

    def get_section(self, section_name):
        parser = self.get_parser()
        section = {
            section_name: dict(parser.items(section_name))
        }
        return section

    def get_sections(self):
        """ 返回值是 dict 类型的 sections, global section 和 user sections 两个类型将分开; keys 可以是正则表达式 """
        parser = self.get_parser()
        sections = {
            'user_sections': {}
        }
        for section_name in parser.sections():
            if self.is_user_section(section_name):
                temp = sections['user_sections']
            else:
                temp = sections
            temp.update(self.get_section(section_name))
        return sections

    def get_empty_section(self, section_type):
        """ secton_type 为 global 或者 user_section """
        parser = self.get_parser()
        section_name = [section_name for section_name in parser.sections() if section_name.startswith(section_type)][0]
        new_section_name = '%s%s' % (section_type, section_type == 'user_section' and self.get_new_section_no() or '')
        return {
            new_section_name: dict.fromkeys(parser.options(section_name), '')
        }

    def validate(self, sections):
        for section_name, section_config in sections.items():
            if not re.match(r'global$|user_section\d+$', section_name):
                raise Exception('Section name 格式错误')
            if section_name == 'global':
                continue
            user_section_config = Config.config['user_section']
            validations = Config.config['validations']
            for option in user_section_config:
                if not validations[user_section_config[option]['validate']].match(section_config[option]):
                    raise Exception('User Section 输入的值出错')
        return True

    def clean(self, sections):
        for section_name in sections:
            for option, value in sections[section_name].items():
                sections[section_name][option] = value.strip()

    def update(self, sections, save=False):
        self.clean(sections)
        if self.validate(sections):
            parser = self.get_parser()
            parser.update(sections)
            self.save(save)

    def delete(self, section_name, save=False):
        parser = self.get_parser()
        if section_name in parser.sections():
            if section_name == 'global':
                raise Exception('不能删除 Global Section')
            if len(parser.sections())<3:
                raise Exception('最后一个 User Section 不能删除')
            parser.remove_section(section_name)
            self.save(save)
        elif self.get_section_no(section_name) not in Config._used_section_nos:
            raise Exception('%s 未定义' % section_name)
        self._delete_section_no(self.get_section_no(section_name))

    def save(self, save=True):
        if save:
            f = open(self.config_filename, 'w', encoding='utf8')
            Config.parser.write(f)
            f.close()
