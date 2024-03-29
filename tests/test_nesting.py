# coding: utf-8

from unittest import TestCase
from nestache import View, debug_tpl, tpl_ignore
import pystache

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

class Debug(View):

    """
    A simple class for which a basic template will be generated
    """

    def debug(self):
        return "Debug"

class Inherited(Base):

    pass

class Ignoreable(View):

    @tpl_ignore
    def ignored(self):
        pass

class TestNesting(TestCase):

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
                         pystache.render(b.template.get(Base), dict(base_var=b.base_var())))

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
                         pystache.render(a.template.get(Base), dict(base_var=a.base_var())))
        self.assertEqual(a.render(Child),
                         pystache.render(a.template.get(Child), dict(child_var=a.child_var())))
        self.assertEqual(a.render(AnotherChild),
                         pystache.render(a.template.get(AnotherChild), dict(another_child_var=a.another_child_var())))

    def test_tpl_nesting(self):
        """Given a few templates, check that nesting works"""
        # Arrange
        a = AnotherChild()
        a.template = { AnotherChild: "{{another_child_var}}",
                       Child:        "{{child_var}}{{ac_tgt}}",
                       Base:         "{{base_var}}{{c_tgt}}" }

        # Act, Assert
        self.assertEqual(a.render(),
                         pystache.render(a.template.get(Base), dict(base_var=a.base_var())) + \
                         pystache.render(a.template.get(Child), dict(child_var=a.child_var())) + \
                         pystache.render(a.template.get(AnotherChild), dict(another_child_var=a.another_child_var())))

    def test_must_use_all(self):
        """A template must use all data supplied if in stricter mode"""
        # Arrange
        b = Base()
        b.template[Base] = " "

        # Act, Assert
        self.assertRaises(KeyError, b.render)

    def test_debug_tpl(self):
        """Generate a debug template"""
        # Arrange
        m = Debug()
        m.template[Debug] = debug_tpl(Debug)

        # Act, Assert
        self.assertEqual(m.render(), """<pre>{'debug': 'Debug'}</pre>""")

    def test_tpl_nest_missing_middle(self):
        """Miss out a template for a superclass layer of Child"""
        # Arrange
        c = Child()
        c.template[Child] = "{{child_var}}"

        # Act, Assert
        c.render(Child) # should work fine
        self.assertRaises(IOError, c.render, Base)
        self.assertRaises(IOError, c.render)

    def test_inherited_methods_ignored(self):
        """Inherited methods shouldn't be noticed (NB. wrt. strict mode)"""
        i = Inherited()
        i.template[Base] = "{{base_var}}{{hook}}"
        i.template[Inherited] = " "
        i.hooks['hook'] = Inherited
        i.render()

class TestPystache(TestCase):

    """
    Tests to ensure integration with Pystache works smoothly.
    """

    def test_global_path_setting(self):
        """Set a global path for searches"""
        path = 'path'
        View.set_global_path(path)
        self.assertEqual(path, pystache.View.template_path)

    def test_tpl_name(self):
        """Ensure that the name is as expected"""
        # Arrange
        b = Base()
        v = pystache.View(context=b)
        v.template_name = b._resolve_name(Base)
        self.assertEqual(v.get_template_name(), 'Base')

class TestIgnored(TestCase):

    """
    Add ability to ignore methods via a decorator.
    """

    def test_ignored(self):
        """Ensure that no errors occur when an ignored method is not used in a template"""
        i = Ignoreable()
        i.template[Ignoreable] = " "
        i.hooks['hook'] = Ignoreable
        i.render()
