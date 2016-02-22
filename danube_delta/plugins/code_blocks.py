
from pelican import signals

from .utils import modify_html


def register():
    signals.content_object_init.connect(process_code_blocks)


def process_code_blocks(article):
    if not article.source_path.endswith('.md'):
        return

    with modify_html(article) as html_tree:
        for pre in html_tree.findall('.//div/pre'):
            pre.getparent().tag = 'pre'
            pre.tag = 'code'
