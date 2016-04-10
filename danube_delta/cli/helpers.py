
import os
import shlex
import random
import subprocess

import click


COMMIT_EMOJIS = [
    ':closed_book:',
    ':green_book:',
    ':blue_book:',
    ':orange_book:',
    ':notebook:',
    ':notebook_with_decorative_cover:',
    ':ledger:',
    ':books:',
    ':pencil2:',
    ':black_nib:',
    ':book:',
    ':memo:',
    ':pencil:',
]


def choose_commit_emoji():
    return random.choice(COMMIT_EMOJIS)


def run(command, env=None, bg=False):
    click.secho(command, fg='magenta', bold=True, err=True)

    options = {
        'env': dict(os.environ, **env) if env else os.environ,
        # 'stdout': subprocess.PIPE,
        'stderr': subprocess.STDOUT,
        'universal_newlines': True,
    }
    if bg:
        return subprocess.Popen(shlex.split(command), **options)

    options['check'] = True
    proc = subprocess.run(shlex.split(command), **options)
    return proc.stdout


def header(text):
    click.secho(text, fg='yellow')


def abort(context):
    click.echo('Aborted!')
    context.exit(1)
