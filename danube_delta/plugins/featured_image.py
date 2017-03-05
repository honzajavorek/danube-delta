import os

from pelican import signals, contents

from .utils import modify_html


def register():
    signals.content_object_init.connect(attach_featured_image)


def attach_featured_image(content):
    if not isinstance(content, contents.Article):
        return

    image = getattr(content, 'image', None)
    if not image:
        with modify_html(content) as html_tree:
            try:
                image = html_tree.findall('.//img')[0].get('src')
            except IndexError:
                image = content.settings.get('DEFAULT_IMAGE')
                if image:
                    image = os.path.join(content.settings['SITEURL'], image)

    if image:
        content.image = image.format(filename=content.get_siteurl())
    else:
        content.image = None
