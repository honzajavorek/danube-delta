
from pelican import signals

from .utils import modify_html


def register():
    signals.content_object_init.connect(attach_featured_image)


def attach_featured_image(content):
    if not content.source_path.endswith('.md'):
        return

    image_url = content.metadata.get('image')
    if not image_url:
        with modify_html(content) as html_tree:
            try:
                image_url = html_tree.findall('.//img')[0].get('src')
            except IndexError:
                image_url = content.settings.get('DEFAULT_IMAGE_URL')

    if image_url:
        content.image = image_url.format(filename=content.get_siteurl())
    else:
        content.image = None
