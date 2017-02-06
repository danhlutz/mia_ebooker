from time import sleep
import string
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests


class Crawler():
    # crawls a Marixst Internet Archive index page to build up
    # a list of content pages

    def __init__(self, target=None):
        # store links to items in an orderedDict
        self.chapters = []
        if target == None:
            self.target = raw_input('What page do you want to ebook?')
        else:
            self.target = target
        self.content = OrderedDict()


    def scrape_index(self, verbose=False):
        # scrapes an index pages and adds to both the index and content objects
        html = requests.get(self.target).text
        soup = BeautifulSoup(html, 'html5lib')
        for link in soup.find_all('a'):
            daughter_url = link.get('href')
            if verbose: print link.get_text()
            if daughter_url == None: continue
            if classify_link(daughter_url) == 'content':
                full_link = combine_links(self.target, daughter_url)
                self.chapters.append(full_link)


    def get_content_page(self, target_url):
        html = requests.get(target_url).text
        # use helper functions to find the starting and ending indexes
        # of the html, then save just that section of the html in an orderedDict
        self.content[target_url] = \
            html[find_section_start(html):find_section_end(html)]


# HELPER FUNCTIONS

# HELPER FUNCTIONS

def fix_unicode(text):
    # replaces a unicode apostrophe with ASCII apostropher
    return text.replace(u"\u2019", "'")


def is_archive(url):
    # verifies if links belong to the Trotsky Internet Archive
    # or point to outside websites or higher level sites
    # first three letters are two dots and a slash
    return (url[-3:] == 'htm' or url[-4:] == 'html') and \
           ((url[:3] == '../' and url[3:5] != '..') or \
            (url[:1] != '.'))


def classify_link(url):
    # classifies a link as either an index or content page
    if is_archive(url) == False:
        return None
    if url[-9:] == 'index.htm' or url[-10:] == 'index.html':
        return 'index'
    else:
        return 'content'


def find_next_to_last_slash(url):
    # used to join shortened urls
    slash = 0
    for i, char in enumerate(url):
        if char == '/':
            next_to_last = slash
            slash = i
    return next_to_last


def find_last_slash(url):
    # used to join shortened urls
    for i, char in enumerate(url):
        if char == '/':
            slash = i
    return slash


def combine_links(mother, daughter):
    # build full urls from shortened urls used on the TIA page
    if daughter[:2] == '..':
        return mother[:find_next_to_last_slash(mother)] + daughter[2:]
    return mother[:find_last_slash(mother) + 1] + daughter


def find_section_start(html):
    for i, character in enumerate(html):
        if html[i:i+3] == '<hr':
            return i


def find_section_end(html):
    last_one = 0

    for i, character in enumerate(html):
        if html[i:i+3] == '<hr':
            last_one = i
    return last_one + find_next_bracket(html[last_one:]) + 1


def find_next_bracket(html):
    for i, character in enumerate(html):
        if character == '>':
            return i


def split_add(full_text, mini_text, position):
    """add mini_text at full_text[position],
    then returns the new full_text and new position"""
    return (full_text[:position] + mini_text + full_text[position:],
           position + len(mini_text))


def go_to_end_and_replace(text, replacement, position):
    while text[position] != '"':
        position += 1
    return split_add(text, replacement, position)


def fix_links(text, replacement, verbose=False):
    position = 0
    while position < len(text):
        if text[position:position + 4] == 'id="':
            if verbose: print 'got an id!'
            text, position = go_to_end_and_replace(text, replacement, position + 4)
        elif text[position:position + 6] == 'name="':
            if verbose: print 'got a name!'
            text, position = go_to_end_and_replace(text, replacement, position + 6)
        elif text[position:position + 6] == 'href="':
            if verbose: print 'got an href!'
            text, position = go_to_end_and_replace(text, replacement, position + 6)
        else:
            position += 1
    return text


# TESTS

def test_fix_unicode():
    apos = u"'"
    apos2 = u"\u2019"
    return fix_unicode(apos) == "'" and fix_unicode(apos2) == "'"


def test_is_archive():
    archives = ['../1924/ffyci-1/app02.htm',
                '../1924/ffyci-1/app03.htm',
                '../1924/ffyci-1/app04.htm',
                '../1924/ffyci-1/ch01.htm',
                'rp03.htm',
                'rp-intro.htm'
                ]
    not_archives = ['../military-pdf/Military-Writings-Trotsky-v1.pdf',
                    '#a1922',
                    '#a1923',
                    '#a1924',
                    '../../../../admin/legal/cc/by-sa.htm'
                    ]
    return sum([is_archive(link) for link in archives]) == len(archives) and \
           sum([is_archive(link) for link in not_archives]) == 0



def test_classify():
    contents = ['../1940/xx/party.htm',
                '../1940/08/last-article.htm',
                '../1940/xx/jewish.htm',
                '../1940/05/stalin.htm'
                ]
    indexes = ['../china/index.htm',
               '../britain/index.htm',
               '../germany/index.htm',
               '../spain/index.htm'
               ]
    not_stuff = ['../../../xlang/trotsky.htm',
                 '../../../admin/volunteers/biographies/dwalters.htm',
                 '#a1934'
                 ]
    return sum([classify_link(link) == 'content' for link in contents]) \
           == len(contents) \
           and sum([classify_link(link) == 'index' for link in indexes]) \
           == len(indexes) \
           and sum([classify_link(link) == None for link in not_stuff]) \
           == len(not_stuff)

def test_find_last_slash():
    return find_last_slash('/') == 0 and \
           find_last_slash('../') == 2 and \
           find_last_slash('../../') == 5


def test_combine():
    return combine_links('http://cnn.com/stuff/here.htm', 'friends.htm') == \
           'http://cnn.com/stuff/friends.htm' and \
           combine_links('http://example.com/mystuff/archives/index.htm', \
                         '../friendex.htm') == \
                         'http://example.com/mystuff/friendex.htm'


def test_scrape_index():
    x = Crawler('https://www.marxists.org/archive/trotsky/1920/terrcomm/index.htm')
    x.scrape_index()
    return x.chapters[4] == \
        u'https://www.marxists.org/archive/trotsky/1920/terrcomm/ch02.htm'


def test_find_section_start():
    html = '''<head><body><class><hr class='class' />
    <p>stuff</p>
    </body>
    <hr >
    </head>
    '''
    print find_section_start(html)
    return find_section_start(html) == 19


def test_find_next_bracket():
    html = '''<head><body><class><hr class='class' />
    <p>stuff</p>
    </body>
    <hr /></head>'''
    return find_next_bracket(html) == 5 and \
        find_next_bracket(html[19:]) == 19

def test_find_section_end():
    html = '''<head><body><class><hr class='class' />
    <p>stuff</p>
    </body>
    <hr /></head>'''
    print html[find_section_end(html):]
    return html[find_section_end(html):] == '</head>'


def test_get_sections_only():
    url = 'https://www.marxists.org/archive/trotsky/1907/1905/ch07.htm'
    x = Crawler(target=url)
    x.get_content_page(url)
    html_start = x.content[url][:15]
    html_end = x.content[url][-4:]
    print html_start
    print html_end
    return html_start == '<hr class="sect' and \
        html_end == 'r />'


def test_split_add():
    text = '<a id="n1" name="n1" href="#f1"><strong>1.</strong></a>'
    text, position = split_add(text, 'abc', 9)
    text, position = split_add(text, 'ABC', position)
    return text == '<a id="n1abcABC" name="n1" href="#f1"><strong>1.</strong></a>'


def test_go_to_end_and_replace():
    text = '<a id="f2" name="f2" href="#n2">[2]</a>'
    text, position = go_to_end_and_replace(text, 'AB', 17)
    print text, position
    return position == 21 and \
        text == '<a id="f2" name="f2AB" href="#n2">[2]</a>'


def test_fix_links():
    text = '<a id="f2" name="f2" href="#n2">[2]</a>'
    new_text = fix_links(text, 'ABC')
    return len(text) + 9 == len(new_text) and \
        new_text == '<a id="f2ABC" name="f2ABC" href="#n2ABC">[2]</a>'


# testing harness
def test_func(func):
    result = func()
    print 'Testing: ', func.__name__, '\t','PASSED: ', result
    if result:
        return 1
    else:
        return 0


def test():
    print '***************************************************'
    print 'BEGIN TESTING'
    print ''
    # list of tests to be run
    func_list = [
        test_fix_unicode,
        test_is_archive,
        test_classify,
        test_find_last_slash,
        test_combine,
        test_scrape_index,
        test_find_section_start,
        test_find_section_end,
        test_find_next_bracket,
        test_get_sections_only,
        test_split_add,
        test_go_to_end_and_replace,
        test_fix_links,
        ]

    # will print individual test results before summing results
    passed = sum([test_func(function) for function in func_list])
    total = len(func_list)
    print ''
    print 'PASSED: ', passed
    print 'FAILED: ', total - passed
    print '***************************************************'
