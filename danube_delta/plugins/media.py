import os
import re
import logging

from lxml import etree
from pelican import signals, contents
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


def process_media(content):
    if not isinstance(content, contents.Article):
        return

    with modify_html(content) as html_tree:
        content_dir = content.settings['PATH']

        for iframe in html_tree.xpath('//iframe'):
            iframe_to_figure(iframe)

        for object in html_tree.xpath('//object'):
            object_to_figure(object)

        for blockquote in html_tree.xpath('//blockquote'):
            tweet_to_figure(blockquote)

        for img in html_tree.xpath('//p[count(img) = 1]/img'):
            img_to_figure(img, content_dir)

        for img in html_tree.xpath('//img'):
            create_img_thumbnail(img, content_dir)
            update_img_classes(img)


def iframe_to_figure(iframe):
    wrap_element(iframe, etree.Element('figure'))


def object_to_figure(object):
    wrap_element(object, etree.Element('figure'))


def img_to_figure(img, content_dir):
    if 'left' in img.classes or 'right' in img.classes:
        return

    figure = img.getparent()
    figure.tag = 'figure'
    figure.classes.add('figure')
    img.classes.update(['figure-img', 'img-fluid'])

    create_figcaption(img, figure)


def tweet_to_figure(blockquote):
    if 'twitter-tweet' not in blockquote.classes:
        return

    wrap_element(blockquote, etree.Element('figure'))


def create_figcaption(img, figure):
    figcaption = etree.Element('figcaption')
    create = False

    if img.tail:
        create = True
        figcaption.text = img.tail
        img.tail = ''

    for sibling in img.itersiblings():
        create = True
        figcaption.append(sibling)

    if not create:
        return

    figcaption.set('class', 'figure-caption')
    figure.append(figcaption)


def update_img_classes(img):
    if 'right' in img.classes:
        img.classes.add('pull-xs-right')
    if 'left' in img.classes:
        img.classes.add('pull-xs-left')
    img.classes.update(['img-fluid', 'img-rounded'])


def create_img_thumbnail(img, content_dir):
    img_src = img.get('src')
    if img_src.startswith('http'):
        logger.warning('Found remotely linked image: %s', img_src)
    else:
        filename = get_image_filename(content_dir, img_src)
        info = get_image_info(filename)
        if info['is_image']:
            if info['needs_click_to_enlarge']:
                wrap_element(img, etree.Element('a', attrib={
                    'href': img_src,
                    'target': '_blank',
                    'title': img.get('alt'),
                }))
            if info['needs_thumbnail']:
                tn_filename = create_thumbnail(filename)
                img.set('src', get_image_src(tn_filename))
        else:
            logger.error('Found non-existing image: %s', img_src)


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
