from lxml import etree
from pelican import signals, contents

from .utils import modify_html, wrap_element


def register():
    signals.content_object_init.connect(enhance_tables)


def enhance_tables(content):
    if not isinstance(content, contents.Article):
        return

    with modify_html(content) as html_tree:
        for table in html_tree.findall('.//table'):
            table.classes.update(['table', 'table-bordered'])
            div = etree.Element('div')
            div.set('class', 'table-responsive')
            wrap_element(table, div)
