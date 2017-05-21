import os


AUTHOR = 'Honza Javorek'

# ABOUT = 'This blog is about kittens and other cute animals.'
# ABOUT_IMAGE = '/images/kitty.jpg'
# ABOUT_HEADING = 'Honza'
# DEFAULT_IMAGE = '/images/default-article-image.jpg'

# SITENAME = 'My Blog'
# SITESUBTITLE = 'The best blog.'

# TWITTER_USERNAME_SITE = 'napyvo'
# TWITTER_USERNAME_AUTHOR = 'honzajavorek'


# Timezone, language
TIMEZONE = 'Europe/Prague'
LOCALE = 'cs_CZ.UTF-8'
DEFAULT_LANG = 'cs'
DEFAULT_DATE_FORMAT = '%x'


# Blog settings
PATH = 'content'
DEFAULT_PAGINATION = False
DEFAULT_CATEGORY = 'blog'
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.headerid': {},
        'markdown.extensions.extra': {},
    },
    'output_format': 'html5',
}


# Outdated articles
OUTDATED_ARTICLE_WARNING = None
OUTDATED_ARTICLE_YEARS = 2


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
    'site.css',
]
EXTRA_PATH_METADATA = {
    'site.css': {'path': 'theme/css/site.css'},
}
USE_SITE_CSS = True


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
THEME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'theme')

from .jinja_filters import JINJA_FILTERS  # NOQA
THEME_STATIC_PATHS = ['static']

GOOGLE_FONTS = ['Roboto Slab', 'Slabo 13px']


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
