# coding=utf8

import configparser, os, re

class Config:
    def __init__(self, config_file='config.cfg', allow_no_value=True, encoding='utf8'):
        self.config_file = config_file
        self.encoding = encoding
        if not os.path.exists(self.config_file):
            open(self.config_file, 'w', encoding=self.encoding).close()
        self.parser = configparser.ConfigParser(allow_no_value=allow_no_value)
        self.parser.read(self.config_file, encoding=self.encoding)

    def get_parser(self):
        return self.parser

    def has_section(self, section_name):
        return section_name in self.get_parser()

    def has_option(self, section_name, option):
        return option in self.get_parser()[section_name]

    def get_value(self, section_name, option):
        return self.get_parser().get(section_name, option)

    def get_section_names(self):
        return self.get_parser().sections()

    def get_options(self, section_name):
        """ 返回指定section的所有option keys. """
        return self.get_parser()[section_name].keys()

    def get_blank_config(self, section_name, flags=0):
        """ 返回匹配section_name的一个空白的config. 参数 section_name 支持正则表达式. 并且自动加上头标志和尾标示 """
        reg = re.compile('^%s$' % section_name, flags)
        parser = sef.get_parser()
        match_section_name = ''
        for section_name in parser:
            if reg.math(section_name):
                match_section_name = section_name
                break
        return dict.fromkeys(self.get_options(), '')

    def get_section(self, section_name):
        parser = self.get_parser()
        section = {
            section_name: dict(parser.items(section_name))
        }
        return section

    def get_sections(self):
        parser = self.parser()
        sections = {}
        for section_name in parser.sections():
            sections[section_name] = self.get_section(section_name)
        return sections

    def update(self, sections, is_save=False):
        parser = self.get_parser()
        update_sections = {}
        for section_name in sections:
            update_section_name = section_name.strip()
            update_config = {}
            for option, value in sections[section_name].items():
                update_config[option.strip()] = value.strip()
            update_sections[update_section_name] = update_config
        parser.update(update_sections)
        self.save(is_save)

    def remove(self, section_name, is_save=False):
        parser = self.get_parser()
        section_name in parser and parser.remove_section(section_name)
        self.save(is_save)

    def clear(self, is_save=False):
        """ 清空所有sections. """
        self.get_parser().clear()
        self.save(is_save)

    def save(self, is_save=True):
        if is_save:
            parser = self.get_parser()
            f = open(self.config_file, 'w', encoding=self.encoding)
            parser.write(f)
            f.close()

    def remove_option(self, section_name, option, is_save=False):
        parser = self.get_parser()
        parser.remove_option(section_name, option)
        slef.save(is_save)
