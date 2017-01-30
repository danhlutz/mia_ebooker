






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
        ]
    # will print individual test results before summing results
    passed = sum([test_func(function) for function in func_list])
    total = len(func_list)
    print ''
    print 'PASSED: ', passed
    print 'FAILED: ', total - passed
    print '***************************************************'