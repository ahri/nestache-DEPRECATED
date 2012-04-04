# coding: utf-8

"""
Simple module built on top of the Mustache templating system.
"""

import inspect
from pprint import pformat
from pystache import View as PystacheView

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
            view = PystacheView(context=self)
            for v in 'template_path', 'template_extension', 'template_name', \
                     'template_file', 'template':
                attr = getattr(self, v)
                if cls in attr:
                    setattr(view, v, attr[cls])

            rendered = view.render()

        if not self.options & View.OPT_IGNORE_UNREQUESTED and \
            self._render_calls != expected_render_calls:

            raise KeyError("Missing calls to: %s" % \
                ', '.join(expected_render_calls -\
                    self._render_calls))

        return rendered

    @staticmethod
    def set_global_path(path):
        PystacheView.template_path = path
