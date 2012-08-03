#!/usr/bin/env python
# coding=utf8

from __future__ import unicode_literals
from __future__ import print_function

from models import Entry, STATUS, KINDS

from google.appengine.ext import db
from google.appengine.api import users

import tornado.web
import tornado.wsgi
import wsgiref.handlers
import logging, datetime, functools, re


def get_now():
    return datetime.datetime.now() + datetime.timedelta(hours=8)

def admin(func):
    """ Decorate with this method to restrict to site admins."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method == "GET":
                self.redirect(self.get_login_url())
                return
            raise tornado.web.HTTPError(403)
        elif not self.current_user.is_admin:
            if self.request.method == "GET":
                self.redirect("/")
                return
            raise tornado.web.HTTPError(403)
        else:
            return func(self, *args, **kwargs)
    return wrapper


class SaveException(Exception):
    pass


class SlugException(Exception):
    pass


class UnknowStatus(Exception):
    pass


class IllegalException(Exception):
    """ 非法操作. """
    pass


class BaseHandler(tornado.web.RequestHandler):
    """ Implements Google Accounts authentication methods."""
    @property
    def is_ajax(self):
        """ Check is ajax request. """
        return bool(self.request.headers.get('X-Requested-With', ''))

    @property
    def is_json(self):
        """ Check is json response. """
        return bool(int(self.get_argument('json', 0)))

    def get_current_user(self):
        user = users.get_current_user()
        if user:
            user.is_admin = users.is_current_user_admin()
        return user

    def get_login_url(self):
        return users.create_login_url(self.request.uri)

    def set_json(self, json):
        """ json 请求时response的内容. """
        self._json = json

    def render_string(self, template_name, **kwargs):
        return super(BaseHandler, self).render_string(template_name, users=users, KINDS=KINDS, STATUS=STATUS, Entry=Entry, **kwargs)

    def render(self, template_name, ajax_template_name=None, **kwargs):
        """ Handle with the ajax request, and let the templates access the users module to generate login URLs. If the parameter json is set, it will response a JSON. """
        if self.is_json:
            return self.write(self._json if isinstance(self._json, dict) else self._json.to_dict())
        if self.is_ajax:
            template_name = ajax_template_name or template_name
        return super(BaseHandler, self).render(template_name, **kwargs)


class Homehandler(BaseHandler):
    """ Home page. """
    def get(self, count=4):
        #entries = Entry.all().order('-published')
        blogs=KINDS.get('blog').entry_set.filter('status =', 'active').order('-published').fetch(count)
        newses=KINDS.get('news').entry_set.filter('status =', 'active').order('-published').fetch(count)
        remarks=KINDS.get('remark').entry_set.filter('status =', 'active').order('-published').fetch(count)
        self.render('index.html', blogs=blogs, newses=newses, remarks=remarks)


class EntryListHandler(BaseHandler):
    """ Show all entries. """
    def get(self, kind_name):
        #entries = Entry.all().order('-published')
        kind = KINDS.get(kind_name)
        items = kind.entry_set.filter('status =', 'active').order('-published')
        div, mod = divmod(items.count(), 20)
        max_page = div + bool(mod)
        page = max(min(int(self.get_argument('page', 1)), max_page), 1)
        self.render('list_show.html', kind=kind, page=page, max_page=max_page, items=items.fetch(20, 20*(page-1)))


class EntryHandler(BaseHandler):
    """ Fetch an entry with slug. """
    def get(self, slug):
        """ Response the entry with the slug. """
        entry = db.Query(Entry).filter('slug =', slug).get()
        if entry.status=='active' or self.current_user and self.current_user.is_admin:
            self.set_json(entry)
            entry.pv_increase()
            self.render('item_show.html', 'modules/%s.html' % entry.entry_kind.name, item=entry)
        else:
            raise Exception('非法操作!')


class ComposeHandler(BaseHandler):
    """ Create, edit and delete an entry. """

    @admin
    def get(self,  entry_key=None):
        """ Just response the entry form or delete an entry. """
        # Check if is delete action and handle it.
        if self._delete(entry_key):
            return
        action = entry_key and 'edit' or 'create'
        entry = entry_key and db.get(entry_key) or None
        kind_name = self.get_argument('kind_name', None)
        self.render('entry_create_or_edit.html', 'modules/entry_form.html', kind=entry and entry.entry_kind or KINDS.get(kind_name), action=action, entry=entry)

    @admin
    def post(self, entry_key=None):
        logging.info(dict(self.request.arguments))
        """ Handle with create, edit and delete actions. """
        # Check if is delete action and handle it.
        if self._delete(entry_key):
            return
        status = self.get_argument('status', None)
        entry = self._create_or_edit(entry_key, status)
        if status not in STATUS:
            raise UnknowStatus('未知状态!')
        self.set_json({'succes': True})
        self.redirect('/entry/%s' % entry.slug)

    def _create_or_edit(self, entry_key, status):
        title, slug, markdown, author, kind_name, reference = self.get_argument('title'), \
            self.get_argument('slug', ''), \
            self.get_argument('content', strip=False), \
            self.get_argument('author', None), \
            self.get_argument('kind_name', None), \
            self.get_argument('reference', None)
        # Check title and markdown is empty.
        if not (title and markdown):
            raise SaveException('标题或者内容为空!')
        if not slug:
            slug = title
        slug = Entry.check_slug(slug, entry_key)
        if slug==None:
            raise SlugException('该 Slug 已经存在!')
        now = get_now()
        if entry_key:
            entry = db.get(entry_key)
            if entry.entry_kind.name != 'blog':
                if not author:
                    raise Exception('作者未知!')
                entry.author = author
            entry.title = title
            entry.slug = slug
            entry.markdown = markdown
            entry.html = Entry.convert(markdown)
            entry.abstract = self._process_abstract(markdown)
            if entry.status == 'draft':
                entry.published = now
            else:
                entry.updated = now
            entry.status = status
        else:
            if kind_name not in KINDS:
                raise Exception('非法类型文章!')
            if kind_name == 'blog':
                author = self.current_user.nickname()
            if not author:
                raise Exception('作者未知!')
            entry = Entry(
                entry_kind = KINDS.get(kind_name),
                author = author or self.current_user.nickname(),
                reference = reference,
                title = title,
                slug = slug,
                markdown = markdown,
                html = Entry.convert(markdown),
                abstract = self._process_abstract(markdown),
                status = status,
                published = now
            )
        entry.put()
        return entry

    def _delete(self, entry_key):
        """ Handle the delete action. """
        if entry_key and self.get_argument('status', None)=='removed':
            entry = db.get(entry_key)
            code = entry.delete_entry()
            self.set_json({'code': code})
            if code < 0:
                self.redirect('/entry/%s' % entry.slug)
            else:
                self.redirect('/')
            return True
        return False

    def _process_abstract(self, markdown, char_count=500):
        markdown = markdown[:char_count]
        return Entry.convert('%s ...' % markdown.rstrip())


class SlugHandler(BaseHandler):
    """ Check the slug is unique. """
    @admin
    def get(self, slug):
        entry_key = self.get_argument('entry_key', None)
        self.write({
            'name': 'slug',
            'validate': Entry.check_slug(slug, entry_key)!=None,
        })


class PreviewHandler(BaseHandler):
    @admin
    def post(self):
        markdown = self.get_argument('markdown', '', strip=False)
        self.write(Entry.convert(markdown))


class FeedHandler(BaseHandler):
    def get(self, limit=10):
        entries = db.Query(Entry).filter('status =', 'active').order('-published').fetch(limit)
        self.set_header("Content-Type", "application/atom+xml")
        self.render("feed.xml", entries=entries)


settings = {
    'title': 'Ross Wan\'s World!',
    'template_path': 'templates',
    'xsrf_cookies': True,
    'cookie_secret': 'mrwlwan#gmail.comgaeweiliangwan81',
}

application = tornado.wsgi.WSGIApplication([
    (r'/', Homehandler),
    (r'/(?P<kind_name>%s)' % '|'.join(KINDS), EntryListHandler),
    (r'/entry/(?P<slug>.+)', EntryHandler),
    (r'/compose/?(?P<entry_key>.*)', ComposeHandler),
    (r'/slug/(?P<slug>.+)', SlugHandler),
    (r'/preview', PreviewHandler),
    (r'/rss', FeedHandler),
], **settings)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
