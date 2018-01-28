import os
import hashlib
import urllib.parse

import requests
from pelican import signals, contents


GRAVATAR_SIZE = 200


def register():
    signals.content_object_init.connect(process_author_info)


def process_author_info(content):
    if not isinstance(content, contents.Article):
        return

    process_twitter(content)
    process_gravatar(content)
    process_about(content)


def process_gravatar(content):
    gravatar = getattr(content, 'gravatar', None)
    if gravatar:
        params = {}

        if content.twitter:
            url = 'https://twitter.com/{}/profile_image?size=original'
            url = url.format(content.twitter)
            try:
                resp = requests.head(url)
                resp.raise_for_status()
                params['d'] = resp.headers['location']
            except Exception:
                pass

        if not params.get('d') and 'DEFAULT_GRAVATAR' in content.settings:
            default_gravatar_url = os.path.join(
                content.settings['SITEURL'],
                content.settings['DEFAULT_GRAVATAR']
            )
            params['d'] = default_gravatar_url

        params['s'] = str(content.settings.get('GRAVATAR_SIZE', GRAVATAR_SIZE))
        gravatar_url = (
            'http://www.gravatar.com/avatar/' +
            hashlib.md5(gravatar.lower().encode('utf-8')).hexdigest()
        )
        gravatar_url += '?' + urllib.parse.urlencode(params)
        content.gravatar = gravatar_url
    else:
        content.gravatar = None


def process_about(content):
    content.about = (
        getattr(content, 'about', None) or
        content.settings.get('ABOUT') or
        None
    )

    about_image = (
        getattr(content, 'aboutimage', None) or
        content.settings.get('ABOUT_IMAGE') or
        None
    )
    content.aboutimage = about_image
    content.about_image = about_image


def process_twitter(content):
    content.twitter = (
        getattr(content, 'twitter', None) or
        content.settings.get('TWITTER_USERNAME_AUTHOR') or
        None
    )
