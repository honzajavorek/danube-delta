
from pelican import signals

from .utils import modify_html


def register():
    signals.content_object_init.connect(process_code_blocks)


def process_code_blocks(content):
    if not content.source_path.endswith('.md'):
        return

    with modify_html(content) as html_tree:
        for pre in html_tree.findall('.//div/pre'):
            pre.getparent().tag = 'pre'
            pre.tag = 'code'
