from subprocess import SubprocessError

import click

from . import blog
from .helpers import run


EXCLUDE = ['.git', '__pycache', 'env', 'venv', 'settings.py']


@blog.command()
@click.pass_context
def lint(context):
    """Looks for errors in source code of your blog"""

    config = context.obj
    try:
        run('flake8 {dir} --exclude={exclude}'.format(
            dir=config['CWD'],
            exclude=','.join(EXCLUDE),
        ))
    except SubprocessError:
        context.exit(1)
