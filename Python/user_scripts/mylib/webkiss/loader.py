# encoding=utf8

import jinja2, tornado.template, os, re

class JinjaLoader(tornado.template.Loader):
    """ For Jinja2 Template System. """
    SPLITE_MACRO_REG = re.compile(r'\s*>\s*')

    def __init__(self, root_directory='.', **kwargs):
        super(JinjaLoader, self).__init__(root_directory, **kwargs)
        self._jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.root))

    def _create_template(self, name, parent=None, globals=None):
        """ 创建Template. 父类的方法多了parent和globals参数. """
        template = self._jinja_env.get_template(name)
        # 跟tornado冲突, 改名为generator
        template.generator = template.generate
        template.generate = template.render
        return template

    def reset(self):
        self._jinja_env.bytecode_cache and self._jinja_env.bytecode_cache.clear()
        super(JinjaLoader, self).reset()

    def config_env(self, **kwargs):
        """ 设置jinja Environment 参数. """
        for key, value in kwargs.items():
            setattr(self._jinja_env, key, value)

    def set_template_path(self, *args):
        """ 设置templates目录. 注意: 仅对FileSystemLoader有效. """
        if args and isinstance(self._jinja_env.loader, jinja2.FileSystemLoader):
            args = [os.path.abspath(arg) for arg in args]
            self._jinja_env.loader.searchpath = args
            self.root = args[-1]
            return True
        return False

    def set_loader(self, loader):
        """ 设置 Jinja Environment loader. """
        self._jinja_env.loader = loader

    def add_filters(self, *args, **kwargs):
        """ 添加Filters. """
        for arg in args:
            self._jinja_env.filters[arg.__name__] = arg
        self._jinja_env.filters.update(kwargs)

    def add_globals(self, **kwargs):
        """ 添加globals. """
        self._jinja_env.globals.update(kwargs)




