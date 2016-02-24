
import os
import re
import logging

from lxml import etree
from pelican import signals
from PIL import Image, ImageFilter

from .utils import modify_html, wrap_element


logger = logging.getLogger(__name__)


IMG_MAX_SIZE = 1024
IMG_CLICK_TO_ENLARGE_THRESHOLD = 700

THUMBNAILS_PATH = 'thumbnails'
THUMBNAIL_SAVE_OPTIONS = {
    'quality': 100,
    'optimize': True,
    'progressive': True,
}


def register():
    signals.content_object_init.connect(process_media)


def process_media(article):
    if not article.source_path.endswith('.md'):
        return

    with modify_html(article) as html_tree:
        content_dir = article.settings['PATH']

        for iframe in html_tree.findall('.//iframe'):
            iframe_to_figure(iframe)
        for object in html_tree.findall('.//object'):
            object_to_figure(object)
        for img in html_tree.findall('.//p/img'):
            img_to_figure(img, content_dir)
        for img in html_tree.findall('.//img'):
            create_img_thumbnail(img, content_dir)


def iframe_to_figure(iframe):
    wrap_element(iframe, etree.Element('figure'))


def object_to_figure(object):
    wrap_element(object, etree.Element('figure'))


def img_to_figure(img, content_dir):
    parent = img.getparent()
    if parent.tag in ('p', 'div'):
        parent.tag = 'figure'
    else:
        parent = wrap_element(img, etree.Element('figure'))

    img_src = img.get('src')
    if not img_src.startswith('http'):
        filename = get_image_filename(content_dir, img_src)
        width = get_image_info(filename)['width']
        if width > IMG_MAX_SIZE:
            width = IMG_MAX_SIZE

        style = 'width: {}px'.format(width)
        img.set('style', style)
        parent.set('style', style)


def create_img_thumbnail(img, content_dir):
    img_src = img.get('src')
    if img_src.startswith('http'):
        logger.warning('Found remotely linked image: %s', img_src)
    else:
        filename = get_image_filename(content_dir, img_src)
        info = get_image_info(filename)
        if info['needs_click_to_enlarge']:
            wrap_element(img, etree.Element('a', attrib={
                'href': img_src,
                'target': '_blank',
                'title': img.get('alt'),
            }))
        if info['needs_thumbnail']:
            tn_filename = create_thumbnail(filename)
            img.set('src', get_image_src(tn_filename))


def get_image_info(filename):
    try:
        width, height = Image.open(filename).size
    except IOError:
        return {'is_image': False}
    return {
        'is_image': True,
        'width': width,
        'height': height,
        'needs_thumbnail': (
            width > IMG_MAX_SIZE or
            height > IMG_MAX_SIZE
        ),
        'needs_click_to_enlarge': (
            width > IMG_CLICK_TO_ENLARGE_THRESHOLD or
            height > IMG_CLICK_TO_ENLARGE_THRESHOLD
        ),
    }


def get_image_filename(content_dir, img_src):
    return os.path.join(content_dir, re.sub(r'.*/images/', 'images/', img_src))


def get_image_src(filename):
    return re.sub(r'.*/images/', '{filename}/images/', filename)


def create_thumbnail(filename):
    tn_dir = os.path.join(os.path.dirname(filename), THUMBNAILS_PATH)
    tn_filename = os.path.join(tn_dir, os.path.basename(filename))

    if not os.path.isfile(tn_filename):
        logger.info('Creating thumbnail for %s', filename)
        os.makedirs(tn_dir, exist_ok=True)
        image = Image.open(filename)
        image.thumbnail((IMG_MAX_SIZE, IMG_MAX_SIZE))
        image.filter(ImageFilter.SHARPEN)
        image.save(tn_filename, image.format, **THUMBNAIL_SAVE_OPTIONS)
    return tn_filename
