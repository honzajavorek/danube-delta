import pytz
import datetime

from pelican import signals, contents


def register():
    signals.content_object_init.connect(calc_outdated_article)


def calc_outdated_article(content):
    if not isinstance(content, contents.Article):
        return

    warning = content.settings.get('OUTDATED_ARTICLE_WARNING')
    years = content.settings.get('OUTDATED_ARTICLE_YEARS')

    if warning and years:
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        years_td = datetime.timedelta(days=365 * years)

        content.is_outdated = content.date < now - years_td
    else:
        content.is_outdated = False
