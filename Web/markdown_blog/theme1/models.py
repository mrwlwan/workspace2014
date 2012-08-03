# coding=utf8

from __future__ import unicode_literals
from __future__ import print_function

from google.appengine.ext import db
from markdown2 import Markdown

from collections import OrderedDict
import re

# 文章状态
STATUS = ('active', 'draft', 'removed')
# 文章类型
KINDS = OrderedDict()

class Kind(db.Model):
    """ 文章类型. 如:日志, 资讯, 新闻等等. """
    name = db.StringProperty(required=True, indexed=True)
    verbose_name = db.StringProperty(required=True)
    order = db.IntegerProperty()


######################################################################
# Just for test
for __kind in Kind.all():
    KINDS.update({__kind.name: __kind})

if not KINDS:
    __test_order = 1
    for i,j in (('blog', '日志'), ('news', '资讯'), ('remark', '奇文')):
        __temp = Kind(name=i,verbose_name=j,order=__test_order)
        __temp.put()
        KINDS.update({i: __temp})
        __test_order += 1
######################################################################


class Entry(db.Model):
    """ Blog, news, and remark entry model."""
    _markdown = Markdown(extras={
        'code-friendly':None,
        'html-classes': {'pre': 'prettyprint linenums'},
    })

    # 文章类型
    entry_kind = db.ReferenceProperty(Kind, required=True)
    # 作者
    author = db.StringProperty(required=True)
    # 标题
    title = db.StringProperty(required=True)
    # slug. SEO 优化用.
    slug = db.StringProperty(required=True, indexed=True)
    # 原 markdown 文本
    markdown = db.TextProperty(required=True)
    # markdown 转换成的 html 文本(caches).
    html = db.TextProperty(required=True)
    # 摘要,在首先上显示
    abstract = db.TextProperty(required=True)
    # 文章的引用链接, 资讯和奇文时用.
    reference =db.StringProperty()
    # 状态
    status = db.StringProperty(required=True, choices=set(STATUS), indexed=True)
    # 发布日期
    published = db.DateTimeProperty(auto_now_add=True)
    # 更新日期
    updated = db.DateTimeProperty()
    # page views
    pv = db.IntegerProperty(default=0)

    @classmethod
    def check_slug(cls, slug, entry=None):
        """ Check the slug is uniqued. The entry parameter can be a entry key. """
        slug = re.sub(r'\s+|\/+', '_', slug.strip())
        if not slug:
            return None
        entry = entry and isinstance(entry, type('')) and db.get(entry) or entry
        if (entry and entry.slug == slug) or db.Query(Entry).filter('slug =', slug).count(1)<1:
            return slug
        return None

    @classmethod
    def convert(cls, markdown):
        """ Convert markdown to html. """
        return Entry._markdown.convert(markdown)

    def delete_entry(self):
        if self.status == 'removed':
            self.delete()
            return 1
        else:
            self.status = 'removed'
            self.put()
            return -1

    def pv_increase(self):
        self.pv += 1
        self.put()

    def to_dict(self):
        """ Translate the database object to dictory. """
        temp = dict([(field, getattr(self, field)) for field in Entry.fields()])
        temp['key'] = self.is_saved() and self.key() or None
        return temp
