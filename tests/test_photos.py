# -*- coding: utf-8 -*-

import os

import pytest
from PIL import Image

from danube_delta.cli import photos


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def test_find_images_handles_usual_types_of_images():
    path = os.path.join(FIXTURES_DIR, 'photos')
    basenames = frozenset([
        os.path.basename(filename)
        for filename in photos.find_images(path)
    ])
    assert basenames == {
        'fire.gif',  # static gif
        'hedgehog.gif',  # animated gif
        'ukulele.jpg',  # jpg
        'fishermen.jpg',  # mpo (jpg with additional metadata)
    }


@pytest.mark.parametrize(
    'basename,result',
    [
        ('fire.gif', False),
        ('hedgehog.gif', True),
        ('ukulele.jpg', False),
    ]
)
def test_is_animated_gif(basename, result):
    filename = os.path.join(FIXTURES_DIR, 'photos', basename)
    with Image.open(filename) as image:
        assert photos.is_animated_gif(image) == result


@pytest.mark.parametrize(
    'basename,result',
    [
        ('fire.gif', 'GIF'),
        ('hedgehog.gif', 'GIF'),
        ('ukulele.jpg', 'JPEG'),
        ('fishermen.jpg', 'JPEG'),
    ]
)
def test_get_format(basename, result):
    filename = os.path.join(FIXTURES_DIR, 'photos', basename)
    with Image.open(filename) as image:
        assert photos.get_format(image) == result


@pytest.mark.parametrize(
    'src_filename',
    photos.find_images(os.path.join(FIXTURES_DIR, 'photos'))
)
def test_import_image_handles_usual_types_of_images(src_filename, tmpdir):
    dest_filename = str(tmpdir.join(os.path.basename(src_filename)))
    photos.import_image(src_filename, dest_filename)

    with Image.open(src_filename) as src_image:
        with Image.open(dest_filename) as dest_image:
            assert (
                photos.is_animated_gif(src_image) ==
                photos.is_animated_gif(dest_image)
            )
