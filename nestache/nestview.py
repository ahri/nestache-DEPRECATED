class View(object):

    """
    """

    template_path = '.'
    template_extension = 'mustache'
    template_name = None
    template_file = None
    template = None
    template_encoding = None

    def render(self):
        raise IOError()
