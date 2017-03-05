import os
from datetime import datetime

import click
from slugify import slugify

from . import blog


@blog.command()
@click.pass_context
def write(context):
    """Starts a new article"""

    config = context.obj

    title = click.prompt('Title')
    author = click.prompt('Author', default=config.get('DEFAULT_AUTHOR'))

    slug = slugify(title)
    creation_date = datetime.now()
    basename = '{:%Y-%m-%d}_{}.md'.format(creation_date, slug)
    meta = (
        ('Title', title),
        ('Date', '{:%Y-%m-%d %H:%M}:00'.format(creation_date)),
        ('Modified', '{:%Y-%m-%d %H:%M}:00'.format(creation_date)),
        ('Author', author),
    )

    file_content = ''
    for key, value in meta:
        file_content += '{}: {}\n'.format(key, value)
    file_content += '\n\n'
    file_content += 'Text...\n\n'
    file_content += '![image description]({filename}/images/my-photo.jpg)\n\n'
    file_content += 'Text...\n\n'

    os.makedirs(config['CONTENT_DIR'], exist_ok=True)
    path = os.path.join(config['CONTENT_DIR'], basename)
    with click.open_file(path, 'w') as f:
        f.write(file_content)

    click.echo(path)
    click.launch(path)
