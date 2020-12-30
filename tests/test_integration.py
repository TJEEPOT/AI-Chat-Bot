#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test scripts for integration testing

Module  : CMP6040-A - Artificial Intelligence, Assignment 2
File    : test_integration.py
Date    : Wednesday 30 December 2020
Desc.   : Testing integration between all systems
History : 30/12/2020 - v1.0 - Create project file
"""
import unittest
from context import model


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
