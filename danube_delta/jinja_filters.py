import re
import json
import urllib.parse
from datetime import date, datetime

import markdown as md
from jinja2 import Markup


JINJA_FILTERS = {}


def register_filter(func):
    JINJA_FILTERS[func.__name__] = func
    return func


@register_filter
def urlencode(s):
    return urllib.parse.quote(s)


@register_filter
def markdown(s):
    return Markup(md.markdown(s, output_format='html5'))


@register_filter
def to_datetime(dt):
    if not isinstance(dt, datetime):
        dt = str(dt)
        try:
            return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(dt, '%Y-%m-%d')
    return dt


@register_filter
def month_name(month_no):
    return [
        'leden', 'únor', 'březen',
        'duben', 'květen', 'červen',
        'červenec', 'srpen', 'září',
        'říjen', 'listopad', 'prosinec',
    ][month_no - 1]


@register_filter
def format_date(dt, format, strip_zeros=True):
    formatted = to_datetime(dt).strftime(format)
    if strip_zeros:
        return re.sub(r'\b0', '', formatted)
    return formatted


@register_filter
def copyright(articles):
    current_year = date.today().year
    years = sorted(article.date.year for article in articles)
    try:
        since_year = years[0]
    except KeyError:
        since_year = current_year

    if current_year == since_year:
        return '© {}'.format(current_year)
    return '© {}—{}'.format(since_year, current_year)


@register_filter
def tojson(*args, **kwargs):
    return json.dumps(*args, **kwargs).replace('/', '\\/')


@register_filter
def has_images(html):
    return re.search(r'<img[^\>]*>', html)


@register_filter
def to_css_class(s):
    return s.replace('_', '-').replace('/', '-')


@register_filter
def prevent_line_breaks(s):
    parts = []
    words = s.split()
    for i, (word1, word2) in enumerate(zip(words, words[1:] + [None])):
        parts.append(word1)
        if word2:
            if len(word2) <= 3:
                parts.append('&nbsp;')
            else:
                parts.append(' ')

    return Markup(''.join(parts))


@register_filter
def google_fonts(fonts):
    url = 'https://fonts.googleapis.com/css?family='
    url += '|'.join([
        urllib.parse.quote_plus(font) + ':400,700' for font in fonts
    ])
    url += '&amp;subset=latin,latin-ext'
    return url
