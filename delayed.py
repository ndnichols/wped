#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by Nathan Nichols on 2008-11-26.
Copyright (c) 2008 InfoLab. All rights reserved.
"""

class Delayed(object):
    """Will delay looking up given arguments until needed."""
    def __init__(self, loader_func, args):
        super(Delayed, self).__init__()
        self.__loader_func = loader_func
        self.__args = args
        self.__lookups = {}
    def __getattr__(self, arg):
        if arg in self.__args:
            self.__loader_func()
            return getattr(self, arg)
        if arg in self.__lookups:
            setattr(self, arg, self.__lookups[arg]())
            return getattr(self, arg)
        return object.__getattribute__(self, arg)
    def lookup(self, arg_name, func):
        self.__lookups[arg_name] = func
        
class Test(Delayed):
    def __init__(self):
        Delayed.__init__(self, self.load, ('foo', 'bar'))
        self.lookup('baz', lambda: 1000000)
    def load(self):
        self.foo = 42
        self.bar = 'barbarbar'

def test():
    c = Test()
    print c.foo
    print c.bar
    print c.baz

if __name__ == '__main__':
    test()

