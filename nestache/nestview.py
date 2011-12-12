import os
from pystache import Template

class View(object):

    """
    """

    lax                = False
    hooks              = {}

    template           = None
    template_file      = None
    template_encoding  = None
    template_name      = None
    template_extension = 'mustache'
    template_path      = '.'

    def _resolve_vartype(self, var, cls):
        try:
            return var.get(cls)
        except AttributeError:
            return var

    def _resolve_template(self, cls):
        return self._resolve_vartype(self.template, cls) or \
            open(self._resolve_full_path(cls)).read()

    def _resolve_file(self, name, cls):
        filename = self._resolve_vartype(self.template_file, cls) or \
            "%(name)s.%(ext)s" % dict(name=name,
                                      ext=self.template_extension)

        return "%(path)s%(sep)s%(filename)s" % dict(path=self.template_path,
                                                    sep=os.sep,
                                                    filename=filename)

    def _resolve_name(self, cls):
        return self._resolve_vartype(self.template_name, cls) or \
            self.__class__.__name__

    def _resolve_full_path(self, cls):
        return self._resolve_file(self._resolve_name(cls), cls)

    def get(self, attr, _):
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
        if cls is None:
            # pick first subclass of View
            cls = self.__class__.mro()[:-2][-1]

        return Template(self._resolve_template(cls), self).render()
