# coding: utf-8

"""
Simple module built on top of the Mustache templating system.
"""

import os
from pystache import Template

class View(object):

    """
    Nestache View: a nested Mustache template View.
    """

    def __init__(self):
        self.lax                = False
        self.hooks              = {}

        self.template           = {}
        self.template_file      = {}
        self.template_encoding  = {}
        self.template_name      = {}
        self.template_extension = {}
        self.template_path      = {}

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
            return self.render(self.hooks[attr])
        except KeyError:
            try:
                return getattr(self, attr)()
            except AttributeError:
                if self.lax:
                    return ''
                raise

    def render(self, cls=None):
        """Render templates for each level of the class hierarchy"""
        if cls is None:
            # pick first subclass of View
            cls = self.__class__.mro()[:-2][-1]

        return Template(self._resolve_template(cls), self).render()
