
import re
import json
from datetime import date, datetime


JINJA_FILTERS = {}


def register_filter(func):
    JINJA_FILTERS[func.__name__] = func
    return func


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
def copyright(year):
    return '© %s–%s' % (year, date.today().year)


@register_filter
def tojson(*args, **kwargs):
    return json.dumps(*args, **kwargs).replace('/', '\\/')


@register_filter
def has_images(html):
    return re.search(r'<img[^\>]*>', html)


@register_filter
def to_css_class(string):
    return string.replace('_', '-').replace('/', '-')
