# coding=utf8

import kiscmd
import colorama
import re, collections

class ReCmd(kiscmd.Cmd):
    def __init__(self, maxlen=10):
        super().__init__()
        self.contents = collections.deque(maxlen=maxlen)

    @property
    def content(self):
        """ 返回当前content. 默认是 contents 的第一个值. """
        return self.content[0] if self.contents else None

    def do_content(self, line):
        """ 显示当前内容. """
        print(self.content)

    def do_set(self, line):
        """ 设置当前内容. """
        content = self.parse_line(line, first=True)
        self.contents.appendleft(content)

    def do_popup(self, line):
        """ popup index. 将 index 位置上的值设置为当前内容. """
        index = self.parse_line(line, first=True)
        if index:
            index = int(index)
            content = self.contents[index]
            del self.contents[index]
            self.contents.appendleft(content)

    def do_list(self, line):
        """ lilst [full]. 显示 contents 列表. 设置参数 full 则显示 content 的全部内容, 否则只显示前面的20个字符. """
        arg = self.parse_line(line, first=True)
        if arg=='full':
            for item in enumerate(self.contents):
                print('%s. %s' % (item))
        else:
            for index, content in enumerate(self.contents):
                print('%s. %s' % (index, content[0:20]))


if __name__ == '__main__':
    cmd = ReCmd()
    cmd.cmdloop()

