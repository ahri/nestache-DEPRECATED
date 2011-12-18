# coding: utf-8

from unittest import TestCase
from nestache import View
from pystache import render

class Base(View):

    """
    A simple base class
    """

    def base_var(self):
        return "base_var"

class Child(Base):

    """
    The child of the base class
    """

    def __init__(self):
        super(Child, self).__init__()
        self.hooks['c_tgt'] = Child

    def child_var(self):
        return "child_var"

class AnotherChild(Child):

    """
    An extra child
    """

    def __init__(self):
        super(AnotherChild, self).__init__()
        self.hooks['ac_tgt'] = AnotherChild

    def another_child_var(self):
        return "another_child_var"

class Magic(View):

    """
    A simple class for which a basic template will be generated
    """

    def magic(self):
        return "Magical"

class Nesting(TestCase):

    """
    Tests around nesting process
    """

    def test_tpl_missing(self):
        """No valid template"""
        # Arrange
        b = Base()
        b.template_file[Base] = 'non-existant'

        # Act, Assert
        self.assertRaises(IOError, b.render)

    def test_tpl_resolve_no_hints(self):
        """Provide as few hints as possible for template name resolution"""
        # Arrange
        b = Base()

        # Act, Assert
        self.assertEqual(b._resolve_full_path(Base), "./Base.mustache")

    def test_tpl_resolve_hint_path(self):
        """Provide the path and resolve the full name"""
        # Arrange
        b = Base()
        b.template_path[Base] = "test"

        # Act, Assert
        self.assertEqual(b._resolve_full_path(Base), "test/Base.mustache")

    def test_tpl_resolve_hint_extension(self):
        """Provide the extension and resolve the full name"""
        # Arrange
        b = Base()
        b.template_extension[Base] = "test"

        # Act, Assert
        self.assertEqual(b._resolve_full_path(Base), "./Base.test")

    def test_tpl_resolve_hint_name(self):
        """Provide the name and resolve the full name"""
        # Arrange
        b = Base()
        b.template_name[Base] = "test"

        # Act, Assert
        self.assertEqual(b._resolve_full_path(Base), "./test.mustache")

    def test_tpl_resolve_hint_file(self):
        """Provide the file and resolve the full name"""
        # Arrange
        b = Base()
        b.template_file[Base] = "test"

        # Act, Assert
        self.assertEqual(b._resolve_full_path(Base), "./test")

    def test_tpl_provide_template(self):
        """Provide the template"""
        # Arrange
        b = Base()
        b.options = View.OPT_IGNORE_MISSING |\
                    View.OPT_IGNORE_UNREQUESTED
        b.template[Base] = "test"

        # Act, Assert
        self.assertEqual(b.render(), "test")

    def test_tpl_substitution(self):
        """Provide the template and a valid substitution"""
        # Arrange
        b = Base()
        b.template[Base] = "{{base_var}}"

        # Act, Assert
        self.assertEqual(b.render(),
                         render(b.template.get(Base), dict(base_var=b.base_var())))

    def test_tpl_substitution_missing(self):
        """Provide the template and an invalid substitution"""
        # Arrange
        b = Base()
        b.template[Base] = "{{base_vr}}"

        # Act, Assert
        self.assertRaises(AttributeError, b.render)

    def test_tpl_substitution_missing_lax(self):
        """Provide the template and an invalid substitution in lax mode"""
        # Arrange
        b = Base()
        b.template[Base] = "{{base_vr}}"
        b.options = View.OPT_IGNORE_MISSING |\
                    View.OPT_IGNORE_UNREQUESTED

        # Act, Assert
        self.assertEqual(b.render(), '')

    def test_tpl_levels(self):
        """Test rendering different levels of a class hierarchy"""
        # Arrange
        a = AnotherChild()
        a.options = View.OPT_IGNORE_UNREQUESTED
        a.template = { AnotherChild: "{{another_child_var}}",
                       Child:        "{{child_var}}",
                       Base:         "{{base_var}}" }

        # Act, Assert
        self.assertEqual(a.render(Base),
                         render(a.template.get(Base), dict(base_var=a.base_var())))
        self.assertEqual(a.render(Child),
                         render(a.template.get(Child), dict(child_var=a.child_var())))
        self.assertEqual(a.render(AnotherChild),
                         render(a.template.get(AnotherChild), dict(another_child_var=a.another_child_var())))

    def test_tpl_nesting(self):
        """Given a few templates, check that nesting works"""
        # Arrange
        a = AnotherChild()
        a.template = { AnotherChild: "{{another_child_var}}",
                       Child:        "{{child_var}}{{ac_tgt}}",
                       Base:         "{{base_var}}{{c_tgt}}" }

        # Act, Assert
        self.assertEqual(a.render(),
                         render(a.template.get(Base), dict(base_var=a.base_var())) + \
                         render(a.template.get(Child), dict(child_var=a.child_var())) + \
                         render(a.template.get(AnotherChild), dict(another_child_var=a.another_child_var())))

    def test_must_use_all(self):
        """A template must use all data supplied if in stricter mode"""
        # Arrange
        b = Base()
        b.template[Base] = ""

        # Act, Assert
        self.assertRaises(KeyError, b.render)

    def test_magic_tpl(self):
        """When a class has the magic template bit
           set it should generate its own template"""
        # Arrange
        m = Magic()
        m.options = View.OPT_MAGIC_TPL

        # Act, Assert
        self.assertEqual(m.render(), """{'magic': 'Magical'}""")
