# coding=utf8

import cmd, inspect, shlex, collections, re, json

class Cmd(cmd.Cmd):
    intro = 'Welcome...'
    prompt = '> '

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_command_func(self, command):
        """ 返回 command 对应的方法. """
        return getattr(self, 'do_%s' % command, None)

    def _get_commands(self):
        """ 返回可用的命令字典. 默认是以 "do_" 开关的方法. """
        return collections.OrderedDict(sorted(((i[3:], j) for i, j in inspect.getmembers(self) if i.startswith('do_'))))

    def _command_help(self, command, func=None, width=None, tab=4):
        """ 返回命令显示的帮助信息.
            @param command(stirng): 命令名. 默认是do_xxx中的xxx.
            @param fucn(function): 命令对应的方法, 默认为do_command.
            @param width(int): 显示的命令名填充长度.
            @param tab(int): width 为 None 时, 显示的命令名后追加的空格数.
        """
        if not func:
            func = self._get_command_func(command)
        if width==None:
            width = len(command) + tab
        doc = func.__doc__ and func.__doc__.strip()
        if doc:
            doc_lines = [line for line in re.split(r'\s*\n\s*', doc)]
            docs = [doc_lines[0]]
            prefix = ' '*width
            for i in range(1, len(doc_lines)):
                docs.append('%s%s' % (prefix, doc_lines[i]))
            doc = '\n'.join(docs)
        else:
            doc = '没找到帮助信息.'

        return '{command:<{width}}{doc}'.format(command=command, width=width, doc=doc)

    def _str_or_json(self, arg):
        """ 返回字符串或者json对象. """
        if (arg.startswith('[') and arg.endswith(']')) or (arg.startswith('{') and arg.endswith('}')):
            return json.loads(arg)
        return arg

    def _eval(self, text, *args, **kwargs):
        text = text.replace('"', '\\"')
        return eval('str("%s")' % text, *args, **kwargs)

    def parse_line(self, line, is_first=False, is_eval=False, is_json=False, **kwargs):
        """ 解析命令行参数, 返回一个类似于 argv 的 list对象.
            如果指定 first 为真值, 则只返回第一个参数字符串.
            line 中若要含有控制字符, 或者双引号, line 字符串必须包含在双引号中.
            kwargs 可指定 shelx.split 的参数.
        """
        argv = shlex.split(line, **kwargs)
        #print(argv)
        if is_first:
            arg = argv[0] if argv else ''
            if is_eval:
                arg = self._eval(arg)
            if is_json:
                arg = self._str_or_json(arg)
            return arg
        else:
            if is_eval:
                argv = [self._eval(arg) for arg in argv]
            if is_json:
                argv = [self._str_or_json(arg) for arg in argv]
            return argv

    def print(self, *args, **kwargs):
        """ 显示文本. """
        try:
            print(*args, **kwargs)
        except:
            print(*[item.__str__().encode('gbk', 'ignore').decode('gbk', 'ignore') for item in args], **kwargs)

    def do_help(self, line):
        """ 显示命令行帮助信息. "help 命令名" 可显示指定命令的帮助信息."""
        target_command = self.parse_line(line, first=True)
        if not target_command:
            print('可用的命令(查看指定的命令: help 命令名):')
            print('='*40)
            commands = self._get_commands()
            print('    '.join(commands.keys()))
            print('\n')
            print('命令描述:')
            print('='*9)
            width = max((len(command) for command in commands.keys())) + 4
            print('\n'.join((self._command_help(command, func, width=width) for command, func in commands.items())))
            print('\n')
        elif self._get_command_func(target_command):
            print('命令描述:')
            print('='*9)
            print(self._command_help(target_command))
            print('\n')
        else:
            print('不支持的命令: %s' % target_command)

    def default(self, line):
        """ 显示不支持命令的信息. """
        print('不支持的命令')

    #def postcmd(self, stop, line):
        #""" 在显示的信息后面追加回车符. """
        #stop != 0 and print('\n')
        #return stop

    def do_exit(self, line):
        """ 退出命令行. """
        return True

    def do_quit(self, line):
        """ 同 exit, 退出命令行. """
        return True

    def emptyline(self):
        """ 空命令处理. """
        return 0
