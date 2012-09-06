# coding=utf8

import pickle, collections, os, itertools, sys
import tkinter as tk
import tkinter.font as font


class Config(collections.UserDict):
    def __init__(self, path, pickler=None, unpickler=None, default={}, options={}):
        """ @param pickler(pickle.Pickler)
            @param unpickler(pickle.Unpickler)
            @param default(dict): 默认的配置.
            @param options(collections.OrderedDict): 用于创建 GUI.
        """
        super().__init__(default)
        self.path = path
        self.pickler = pickler or pickle.Pickler
        self.unpickler = unpickler or pickle.Unpickler
        self.options = options

    def load(self, *args, **kwargs):
        if os.path.exists(self.path):
            with open(self.path, 'rb') as f:
                try:
                    self.update(self.unpickler(f, *args, **kwargs).load())
                except:
                    print('加载失败或者配置文件为空.')

    def save(self, *args, **kwargs):
        with open(self.path, 'wb') as f:
            try:
                self.pickler(f, *args, **kwargs).dump(self.data)
            except:
                print('保存配置失败.')

    def show_gui(self, options={}):
        """ @param options(collections.OrderedDict): 字段格式. {'option': {'get':取值方法(callable/str), 'set': 存值方法(callable/str), 'pre_set': 用于set(callable), 'widget': 对应的tk类, 'help': 帮助文本}, ...}."""
        options = collections.ChainMap(options, self.options)
        self._options = options
        fields = {}
        self._fields = fields
        root = tk.Tk()
        self._root = root
        root.title('配置')
        root.minsize(300, 0)
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=0)
        root.columnconfigure(2, weight=0)
        root.columnconfigure(3, weight=1)
        root.resizable(1, 0)
        gui_font = font.Font(root, size=12)
        help_font = font.Font(root, size=10)
        row_count = itertools.count(0)
        for option, config in options.items():
            row = next(row_count)
            tk.Label(root, text=option, font=gui_font).grid(row=row, column=0, sticky=tk.E)
            if config.get('widget'):
                temp = getattr(tk, config.get('widget'))(root, font=gui_font)
            else:
                temp = tk.Entry(root, font=gui_font)
            fields[option] = temp
            temp.grid(row=row, column=1, columnspan=3, sticky=tk.EW, padx=6, pady=3)
            if config.get('help'):
                tk.Label(root, text=config.get('help'), font=help_font).grid(row=next(row_count), column=1, columnspan=3, sticky=tk.W)
        self._reset()
        row = next(row_count)
        tk.Button(root, text='保存', font=gui_font, command=self._save).grid(row=row, column=1, padx=6, pady=3)
        tk.Button(root, text='重置', font=gui_font, command=self._reset).grid(row=row, column=2)
        tk.Button(root, text='取消', font=gui_font, command=root.destroy).grid(row=row, column=3, sticky=tk.W, padx=6)
        root.mainloop()
        self._root = None
        self._options = {}
        self._fields = {}

    def _reset(self):
        """ Reset 事件处理. """
        fields = self._fields
        options = self._options
        for option, config in options.items():
            value = self.get(option)
            get_method = config.get('get')
            if not get_method:
                if value == None:
                    value = ''
                elif isinstance(value, bool):
                    value = str(int(value))
            elif callable(get_method):
                value = get_method(value)
            elif isinstance(get_method, str):
                value = getattr(value, get_method)()

            fields.get(option).delete(0, tk.END)
            fields.get(option).insert(tk.END, str(value))

    def _save(self):
        """ Save 事件处理. 须显式调用save方法存对象入文件. """
        for option, widget in self._fields.items():
            config = self._options.get(option)
            try:
                value = widget.get()
            except:
                value = widget.get(1.0, tk.END)
            set_method = config.get('set')
            pre_set_method = config.get('pre_set')
            if set_method:
                if pre_set_method:
                    value = pre_set_method(value)
                if callable(set_method):
                    self[option] = set_method(value)
                elif isinstance(set_method, str):
                    getattr(self[option], set_method)(value)
            else:
                self[option] = value
        self._root.destroy()

    def ckeck_arg(self, options={}):
        if sys.argv in set(['-c', '--config']):
            self.show_gui(options)
