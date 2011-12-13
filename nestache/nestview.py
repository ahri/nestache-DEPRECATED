# coding: utf-8

"""
Simple module built on top of the Mustache templating system.
"""

import os
import inspect
from pystache import Template

class View(object):

    """
    Nestache View: a nested Mustache template View.
    """

    ERR_NEVER            = 0b00
    ERR_MISSING_DATA     = 0b01
    ERR_UNREQUESTED_DATA = 0b10
    ERR_ALWAYS           = ERR_MISSING_DATA | ERR_UNREQUESTED_DATA

    def __init__(self):
        self.strictness         =  View.ERR_ALWAYS

        self.hooks              = {}

        self.template           = {}
        self.template_file      = {}
        self.template_encoding  = {}
        self.template_name      = {}
        self.template_extension = {}
        self.template_path      = {}

        self._render_calls      = None

    def _resolve_template(self, cls):
        if cls in self.template:
            return self.template.get(cls)

        return open(self._resolve_full_path(cls)).read()

    def _resolve_full_path(self, cls):
        return self._resolve_file(self._resolve_name(cls), cls)

    def _resolve_name(self, cls):
        return self.template_name.get(cls, self.__class__.__name__)

    def _resolve_file(self, name, cls):
        filename = self.template_file.get(cls, \
            "%(name)s.%(ext)s" % dict(name=name,
                                      ext=self.template_extension.get(cls, 'mustache')))

        return "%(path)s%(sep)s%(filename)s" % dict(path=self.template_path.get(cls, '.'),
                                                    sep=os.sep,
                                                    filename=filename)

    def get(self, attr, _):
        """Quack like a dict."""
        try:
            val = self.render(self.hooks[attr])
        except KeyError:
            try:
                val = getattr(self, attr)()
            except AttributeError:
                if not self.strictness & View.ERR_MISSING_DATA:
                    val = ''
                else:
                    raise

        self._render_calls.add(attr)
        return val

    def _func_names(self, cls):
        return set([f.__name__ for f in cls.__dict__.values()
             if inspect.isfunction(f) and
                 not f.func_name.startswith('_')])

    def render(self, cls=None):
        """Render templates for each level of the class hierarchy"""
        if cls is None:
            # pick first subclass of View
            cls = self.__class__.mro()[:-2][-1]

        self._render_calls = set()
        expected_render_calls = self._func_names(cls)
        rendered = Template(self._resolve_template(cls), self).render()
        if self.strictness & View.ERR_UNREQUESTED_DATA and self._render_calls != expected_render_calls:
            raise KeyError("Missing calls to: %s" % \
                ', '.join(expected_render_calls -\
                    self._render_calls))

        return rendered
