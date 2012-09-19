# coding=utf8

import kiscmd
import colorama
import re, collections
from urllib.parse import urlparse

class ReCmd(kiscmd.Cmd):
    def __init__(self, maxlen=10):
        super().__init__()
        self.contents = collections.deque(maxlen=maxlen)
        self._opener = None

    @property
    def opener(self):
        """ 返回 Opener 对象. """
        if self._opener:
            return self._opener
        else:
            import kisopener
            self._opener = kisopener.Opener()
            return self._opener

    @property
    def content(self):
        """ 返回当前content. 默认是 contents 的第一个值. """
        return self.contents[0] if self.contents else None

    def _slice(self, start, end=None):
        """ 返回当前内容的子字符串. """
        return self.content[slice(int(start), int(end) if end!=None else None)]

    def do_content(self, line):
        """ 显示当前内容. """
        self.print(self.content)

    def do_len(self, line):
        """ 当前内容的长度. """
        if self.content!=None:
            print(len(self.content))

    def do_slice(self, line):
        """ slice start [end]. 显示当前内容的子字符串. """
        argv = self.parse_line(line)
        if argv:
            self.print(self._slice(*argv))

    def do_set(self, line):
        """ 设置当前内容. """
        content = self.parse_line(line, first=True)
        self.contents.appendleft(content)

    def do_sliceset(self, line):
        """ 将子字符串设置为当前内容. """
        argv = self.parse_line(line)
        if argv:
            self.contents.appendleft(self._slice(*argv))

    def do_remove(self, line):
        """ remove index. 删除 index 位置上的内容. """
        index = self.parse_line(line, first=True)
        if index:
            del self.contents[int(index)]

    def do_popup(self, line):
        """ popup index. 将 index 位置上的内容设置为当前内容. """
        index = self.parse_line(line, first=True)
        if index:
            index = int(index)
            content = self.contents[index]
            del self.contents[index]
            self.contents.appendleft(content)

    def do_list(self, line):
        """ lilst [full]. 显示 contents 列表. 设置参数 full 则显示 content 的全部内容, 否则只显示前面的80个字符. """
        arg = self.parse_line(line, first=True)
        if arg=='full':
            for item in enumerate(self.contents):
                self.print('%s. %s' % (item))
        else:
            for index, content in enumerate(self.contents):
                self.print('%s. %s' % (index, content[0:80]))

    def do_fetch(self, line):
        """ fetch url [param data...]. 抓取网页内容为当前内容. 注意: 其后一般需要运行命令 encode, 将内容转为 unicode. """
        argv = self.parse_line(line, json=True)
        if argv:
            url = argv[0]
            if not urlparse(url).scheme:
                url = 'http://' + url
                argv[0] = url
            content = self.opener.urlopen(*argv)
            if content:
                self.contents.appendleft(content.read())
                print('抓取成功!')
            else:
                print('抓取失败或者内容为空.')

    def do_encode(self, line):
        """ encode [codec]. 将当前内容转为 unicode. 默认 codec 为 utf8. """
        codec = self.parse_line(line) or ['utf8', 'strict']
        try:
            self.contents.appendleft(self.contents.popleft().decode(*codec))
        except:
            print('编码错误!')


if __name__ == '__main__':
    colorama.init(autoreset=True)
    cmd = ReCmd()
    cmd.cmdloop()

