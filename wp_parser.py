#!/usr/bin/env python
# encoding: utf-8
"""
wp_parser.py

Created by Nathan Nichols on 2008-11-18.
Copyright (c) 2008 InfoLab. All rights reserved.
"""

import time
import re
import xml.dom.minidom

#test

total_entries = 7278278

char_map = {8722: '-', 8211: '-', 8212: '-', 8213: '-', 8216: "'", 8217: "'", 8218: ',', 8220: '"', 8221: '"', 8230: '...', 187: '>>', 7789: 't', 171: '<<', 173: '-', 180: "'", 699: "'", 7871: 'e', 192: 'A', 193: 'A', 194: 'A', 195: 'A', 196: 'A', 197: 'A', 198: 'Ae', 199: 'C', 200: 'E', 201: 'E', 202: 'E', 203: 'E', 204: 'I', 7885: 'o', 206: 'I', 205: 'I', 208: 'D', 209: 'N', 210: 'O', 211: 'O', 212: 'O', 213: 'O', 214: 'O', 215: 'x', 216: 'O', 217: 'U', 218: 'U', 207: 'I', 220: 'U', 221: 'Y', 223: 'S', 224: 'a', 225: 'a', 226: 'a', 227: 'a', 228: 'a', 229: 'a', 230: 'ae', 231: 'c', 232: 'e', 233: 'e', 234: 'e', 235: 'e', 236: 'i', 237: 'i', 238: 'i', 239: 'i', 240: 'o', 241: 'n', 242: 'o', 243: 'o', 244: 'o', 245: 'o', 246: 'o', 247: '/', 248: 'o', 249: 'u', 250: 'u', 251: 'u', 252: 'u', 253: 'y', 255: 'y', 256: 'A', 257: 'a', 259: 'a', 261: 'a', 263: 'c', 268: 'C', 269: 'c', 279: 'e', 281: 'e', 283: 'e', 287: 'g', 219: 'U', 298: 'I', 299: 'i', 304: 'I', 305: 'i', 322: 'l', 324: 'n', 332: 'O', 333: 'o', 335: 't', 337: 'o', 339: 'oe', 345: 'r', 346: 'S', 347: 's', 351: 's', 352: 'S', 353: 's', 355: 'c', 363: 'u', 367: 'u', 378: 'z', 379: 'Z', 381: 'Z', 382: 'z', 924: 'M', 451: '!'}

def safeStr(text):
    import unicodedata
    if type(text) is not unicode:
        try:
            text = unicode(text, "utf-8", 'ignore')
        except TypeError, e:
            pass
        text = unicodedata.normalize('NFKD', text)
    ret = [c if ord(c) < 128 else char_map.get(ord(c), '') for c in text]
#    ret = ''.join(ret)
#    ret = ret.encode('ASCII', 'ignore')
    # return ret
    return ''

_start_page_regex = re.compile(r'<page>')
_end_page_regex = re.compile(r'</page>')
_wp_link_regex = re.compile(r'\[\[([^\|^\]]*)(?:\|([^\]]*))?\]\]')
_template_regex = re.compile(r'{{([^}]*)}}')
_language_regex = re.compile(r'^[a-z\-]+:') #matches things like 'fr:foobar'

def _regex_iter(regex):
    def foo(text):
        i = 0
        while True:
            match = regex.search(text, i)
            if match is None:
                return
            i = match.end()
            yield match.groups()
    return foo

_getLinks = _regex_iter(_wp_link_regex)
_getTemplates = _regex_iter(_template_regex)
def _getTemplate(text):
    match = _template_regex.search(text)
    return match.groups() if match is not None else None
def _getLink(text):
    match =  _wp_link_regex.search(text)
    return match.groups() if match is not None else None    

class RedirectPage(object):
    """Represents a redirectpage from Wikipedia"""
    def __init__(self, title, text):
        super(RedirectPage, self).__init__()
        self.title = title
        self.target = ''
        self.explanations = []
        self._parseText(text)
    def _parseText(self, text):
        self.target = _getLink(text)[0]
        self.explanations = list(_getTemplates(text))
    def __str__(self):
        return 'Redirect page from %s to %s, explanations are %s' % (self.title, self.target, self.explanations)
        
class CategoryPage(object):
    """One of the category pages"""
    def __init__(self, title, text):
        super(CategoryPage, self).__init__()
        self.title = title
        self.text = ''
        self.categories = []
        self._parseText(text)
    def _parseText(self, text):
        self.text = text
        all_links = _getLinks(text)
        for target, surface in all_links:
            if target.startswith('Category'):
                self.categories.append(target)
    def __str__(self):
        ret = ''
        ret += 'Category page with title %s\n' % (self.title)
        ret += 'Parent categories:\n'
        for category in self.categories:
            ret += '   %s\n' % (category)
        return ret

class EntryPage(object):
    '''Represents a normal entry page in WP.'''
    def __init__(self, title, text):
        super(EntryPage, self).__init__()
        self.title = title
        self.links = [] #list of (target, surface) tuples
        self.categories = []
        self.text = ''
        self.intro_text = ''
        self._parseText(text)
    def _parseText(self, text):
        self.text = text
        all_links = _getLinks(self.text)
        for target, surface in all_links:
            if surface is None:
                surface = target
            if target.startswith('Category'):
                self.categories.append(target)
            elif target.startswith('Image'):
                continue
            elif _language_regex.search(target) is not None:
                continue
            else:
                self.links.append((target, surface))

    def __str__(self):
        ret = ''
        ret += 'Entry page for %s\n' % (self.title)
        ret += 'Outgoing links:\n'
        for target, surface in self.links:
            ret += '  %s <= %s\n' % (target, surface)
        ret += 'Categories:\n'
        for category in self.categories:
            ret += '  %s\n' % (category)
        return ret
        
i = 0
def Page(lines):
    global i
    print i
    i += 1
    #return
    page_dom = xml.dom.minidom.parseString(' '.join(lines))
    page_title = page_dom.getElementsByTagName('title')[0].childNodes[0].data
    page_text = page_dom.getElementsByTagName('text')[0].childNodes[0].data
    page_title, page_text = safeStr(page_title), safeStr(page_text)
    # print 'http://en.wikipedia.org/wiki/' + page_title
    # print page_text[:100]
    if page_text.startswith('#REDIRECT'):
        return RedirectPage(page_title, page_text)
    elif page_title.startswith('Category'):
        return CategoryPage(page_title, page_text)
    else:
        return EntryPage(page_title, page_text)
    # TODO Implement the other page types   
    return None
    

class Parser:
    def __init__(self, filename):
        """docstring for __init__"""
        self.filename = filename
    def getEntries(self):
        o = open(self.filename, 'r')
        in_page = False
        i = 0
        ret = []
        while True:
            line = o.readline()
            if not line: #done parsing whole xml file
                return
            
            if _start_page_regex.search(line) is not None:
                in_page = True
            if _end_page_regex.search(line) is not None:
                i += 1
                in_page = False
                ret.append(line)
                yield (Page(ret))
                if i == 10000:
                    break
                # raw_input()
                ret = []
                continue
                
            if in_page:
                ret.append(line)
            
if __name__ == '__main__':
    start_time = time.time()
    c = Parser('/Users/nate/Programming/wped/wikipedia.xml')
    for page in c.getEntries():
        if isinstance(page, CategoryPage):
            print page
    print 'getting to 10000 took %s' % (time.time() - start_time)

        
    