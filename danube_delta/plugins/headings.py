from lxml import etree
from pelican import signals, contents

from .utils import modify_html


def register():
    signals.content_object_init.connect(enhance_headings)


def enhance_headings(content):
    if not isinstance(content, contents.Article):
        return

    with modify_html(content) as html_tree:
        for query in ['.//h1[@id]', './/h2[@id]', './/h3[@id]', './/h4[@id]']:
            for heading in html_tree.findall(query):
                add_permalink(heading)


def add_permalink(heading):
    a = etree.Element('a')
    a.text = '#'
    a.set('href', '#{}'.format(heading.get('id')))
    a.set('title', 'Trvalý odkaz na tento nadpis')
    small = etree.Element('small')
    small.set('class', 'permalink')
    small.append(a)
    heading.append(small)
