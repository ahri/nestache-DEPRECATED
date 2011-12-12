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

class AnotherChild(Child):

    """
    An extra child
    """

class Nesting(TestCase):

    """
    Tests around nesting process
    """

    def test_tpl_missing(self):
        """No valid template"""
        # Arrange, Act, Assert
        self.assertRaises(IOError, Base().render)
