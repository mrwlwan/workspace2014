# coding=utf8

import cmd, inspect, shlex, collections, re

class Cmd(cmd.Cmd):
    intro = 'Welcome...'
    prompt = '> '

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
            func = getattr(self, 'do_%s' % command)
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

        return '{command:<{width}}{doc}\n'.format(command=command, width=width, doc=doc)

    def parse_line(self, line, first=False, **kwargs):
        """ 解析命令行参数, 返回一个类似于 argv 的 list对象.
            如果指定 first 为真值, 则只返回第一个参数字符串.
            kwargs 可指定 shelx.split 的参数.
        """
        argv = shlex.split(line, **kwargs)
        return (argv[0] if argv else '') if first else argv

    def do_help(self, line):
        """ 显示命令行帮助信息. "help 命令名" 可显示指定命令的帮助信息."""
        target_command = self.parse_line(line, first=True)
        if not target_command:
            print('可用的命令(查看指定的命令: help 命令名):')
            print('='*40)
            print('\n命令描述:')
            print('='*9)
            commands = self._get_commands()
            width = max((len(command) for command in commands.keys())) + 4
            for command, func in commands.items():
                print(self._command_help(command, func, width=width))
        else:
            print('\n命令描述:')
            print('='*9)
            print(self._command_help(command))

    def do_exit(self, line):
        """ 退出命令行. """
        return True

    def do_quit(self, line):
        """ 同 exit, 退出命令行. """
        return True

    def emptyline(self):
        """ 空命令处理. """
        pass
