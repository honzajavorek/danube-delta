from pelican import signals, contents

from .utils import modify_html


def register():
    signals.content_object_init.connect(make_summary_plain)


def make_summary_plain(content):
    if not isinstance(content, contents.Article):
        return

    content._summary = content._content
    with modify_html(content, prop='_summary') as html_tree:
        queries = [
            '//iframe', '//object', '//p[count(img) = 1]',
            '//img', '//figure',
        ]
        for query in queries:
            for element in html_tree.xpath(query):
                element.getparent().remove(element)
