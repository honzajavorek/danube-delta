
import os


AUTHOR = 'Honza Javorek'


# Timezone, language
TIMEZONE = 'Europe/Prague'
LOCALE = 'cs_CZ.UTF-8'
DEFAULT_LANG = 'cs'
DEFAULT_DATE_FORMAT = '%x'


# Blog settings
PATH = 'content'
DEFAULT_PAGINATION = 5
SUMMARY_MAX_LENGTH = 80
DEFAULT_CATEGORY = 'blog'
MD_EXTENSIONS = ['codehilite(css_class=highlight)', 'headerid', 'extra']


# URL and save paths settings
ARTICLE_URL = '{slug}'
ARTICLE_SAVE_AS = '{slug}.html'
ARTICLE_LANG_URL = '{slug}-{lang}'
ARTICLE_LANG_SAVE_AS = '{slug}-{lang}.html'
PAGE_URL = '{slug}'
PAGE_SAVE_AS = '{slug}.html'
PAGE_LANG_URL = '{slug}-{lang}'
PAGE_LANG_SAVE_AS = '{slug}-{lang}.html'
URL_EXT = ''
FILENAME_METADATA = r'(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>.*)'


# Static paths will be copied under the same name
STATIC_PATHS = [
    'images',
    'files',
    'robots.txt',
    'favicon.ico',
    'CNAME',
]


# Generating
IGNORE_FILES = ['.#*', '.DS_Store']
DELETE_OUTPUT_DIRECTORY = True


# Feeds
FEED_ALL_ATOM = 'feed.xml'
FEED_MAX_ITEMS = 50

CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


# Plugins
from .plugins import PLUGINS  # NOQA


# Theming
from .jinja_filters import JINJA_FILTERS  # NOQA
THEME_STATIC_PATHS = ['static']

MENUITEMS = []
LINKS = []
SOCIAL = []


# Development
if os.environ.get('PRODUCTION'):
    PRODUCTION = True
    DEVELOPMENT = False

    RELATIVE_URLS = False
else:
    PRODUCTION = False
    DEVELOPMENT = True

    SITEURL = 'http://localhost:8000'
    RELATIVE_URLS = True

    URL_EXT = '.html'
    ARTICLE_URL += URL_EXT
    ARTICLE_LANG_URL += URL_EXT
    PAGE_URL += URL_EXT
    PAGE_LANG_URL += URL_EXT
