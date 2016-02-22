
from lxml import etree
from pelican import signals

from .utils import modify_html


def register():
    signals.content_object_init.connect(add_permalinks)


def add_permalinks(article):
    if not article.source_path.endswith('.md'):
        return

    with modify_html(article) as html_tree:
        for query in ['.//h1[@id]', './/h2[@id]', './/h3[@id]', './/h4[@id]']:
            for heading in html_tree.findall(query):
                a = etree.Element('a')
                a.text = '#'
                a.set('href', '#{}'.format(heading.get('id')))
                a.set('title', 'Trvalý odkaz na tento nadpis')
                small = etree.Element('small')
                small.set('class', 'permalink')
                small.append(a)
                heading.append(small)
