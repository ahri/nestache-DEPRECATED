# coding: utf-8

"""
Simple module built on top of the Mustache templating system.
"""

import os
import inspect
from pprint import pformat
from pystache import Template

def func_names_on_class(cls):
    """Given a class, find out the names of
       the public functions defined on it"""
    return set([f.__name__ for f in cls.__dict__.values()
            if inspect.isfunction(f) and
                not f.func_name.startswith('_')])

def debug_tpl(cls):
    """Generate a simple template using prettyprint"""
    d = {}
    for f in func_names_on_class(cls):
        d[f] = "{{%s}}" % f

    return "<pre>%s</pre>" % pformat(d)

class SandboxCallState(object):

    """
    This is really dirty but it's needed because we need to maintain
    sandboxed state-awareness whilst sub-templates are rendered using the same
    object -- which would otherwise trample on the _view_render_calls set.

    Not happy with this.
    """

    def __init__(self, view):
        self.view = view
        self.tmp = None

    def __enter__(self):
        self.tmp = self.view._render_calls

    def __exit__(self, *_):
        self.view._render_calls = self.tmp

class View(object):

    """
    Nestache View: a nested Mustache template View.
    """

    OPT_NONE               = 0000
    OPT_IGNORE_MISSING     = 0001
    OPT_IGNORE_UNREQUESTED = 0010

    def __init__(self):
        self.options            =  View.OPT_NONE

        self.hooks              = {}

        self.template           = {}
        self.template_file      = {}
        self.template_encoding  = {}
        self.template_name      = {}
        self.template_extension = {}
        self.template_path      = {}

        self._render_calls      = None

    def _resolve_template(self, cls):
        """Either provide specified content or
           fall back to content from a file"""
        if cls in self.template:
            return self.template.get(cls)

        return open(self._resolve_full_path(cls)).read()

    def _resolve_full_path(self, cls):
        """Determine the full path of a file"""
        return self._resolve_file(self._resolve_name(cls), cls)

    def _resolve_name(self, cls):
        """Either provide a specified name, or
           fall back to the name of the class"""
        return self.template_name.get(cls, self.__class__.__name__)

    def _resolve_file(self, name, cls):
        """Given a name, provide the filename with
           the specified (or defaulted) path"""
        ext = self.template_extension.get(cls, 'mustache')

        filename = self.template_file.get(cls, \
            "%(name)s.%(ext)s" % dict(name=name,
                                      ext=ext))

        path = self.template_path.get(cls, '.')

        return "%(path)s%(sep)s%(filename)s" % dict(path=path,
                                                    sep=os.sep,
                                                    filename=filename)

    def get(self, attr, _):
        """Quack like a dict."""
        if attr in self.hooks:
            val = self.render(self.hooks[attr])
        else:
            try:
                val = getattr(self, attr)()
            except AttributeError:
                if self.options & View.OPT_IGNORE_MISSING:
                    val = ''
                else:
                    raise

        self._render_calls.add(attr)
        return val

    def render(self, cls=None):
        """Render template for specified class"""
        if cls is None:
            # pick first subclass of View
            cls = self.__class__.mro()[:-2][-1]

        self._render_calls = set()
        expected_render_calls = func_names_on_class(cls)

        with SandboxCallState(self):
            rendered = Template(self._resolve_template(cls), self).render()

        if not self.options & View.OPT_IGNORE_UNREQUESTED and \
            self._render_calls != expected_render_calls:

            raise KeyError("Missing calls to: %s" % \
                ', '.join(expected_render_calls -\
                    self._render_calls))

        return rendered
