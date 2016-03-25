
from pelican import signals


def register():
    signals.content_object_init.connect(process_author_info)


def process_author_info(content):
    if not content.source_path.endswith('.md'):
        return

    content.about = (
        getattr(content, 'about', None) or
        content.settings.get('ABOUT') or
        None
    )
