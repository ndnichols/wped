#!/usr/bin/env python
# encoding: utf-8
"""
wp_import.py

This is the main thing that reads in the XML and fills the db.

Created by Nathan Nichols on 2008-12-01.
Copyright (c) 2008 InfoLab. All rights reserved.
"""

import mysql
import wp_parser
from wp_parser import *

_db = None

def initDB():
    global _db
    _db = mysql.Connection('wikipedia')

def ensureDB():
    """Makes sure the DB tables are all setup"""
    _db.execute('CREATE TABLE IF NOT EXISTS categories (id INT NOT NULL AUTO_INCREMENT, title CHAR(255), PRIMARY KEY(id));')
    _db.execute('CREATE TABLE IF NOT EXISTS entries (id INT NOT NULL AUTO_INCREMENT, title CHAR(255), PRIMARY KEY(id));')
    
def clearEverything():
    _db.execute('DROP TABLES IF EXISTS categories, entries;')
    
def step1():
    '''Cut a hole in the box.'''
    entries, categories = {}, {}
    c = Parser('/Users/nate/Programming/wped/wikipedia.xml')
    for i, page in enumerate(c.getEntries()):
        if isinstance(page, CategoryPage):
            title = page.title[:255]
            if title not in categories:
                _db.execute('INSERT INTO categories (title) VALUES (%s)', title)
                categories[title] = True
        elif isinstance(page, EntryPage):
            title = page.title[:255]
            if title not in entries:
                _db.execute('INSERT INTO entries (title) VALUES (%s)', title)
                entries[title] = True
        if i % 10000 == 0:
            print '%s/%s' % (i, wp_parser.totalEntries)
            

def main():
    initDB()
    clearEverything()
    ensureDB()
    step1()
    



if __name__ == '__main__':
    main()

