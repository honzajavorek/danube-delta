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


def run(command, env=None, bg=False, capture=False):
    options = {
        'env': dict(os.environ, **env) if env else os.environ,
        'universal_newlines': True,
    }
    if capture:
        options['stdout'] = subprocess.PIPE
        options['stderr'] = subprocess.STDOUT
    if bg:
        return subprocess.Popen(shlex.split(command), **options)

    options['check'] = True
    proc = subprocess.run(shlex.split(command), **options)
    return proc.stdout


def header(text):
    click.secho(text, fg='yellow', bold=True)


def abort(context):
    click.echo('Aborted!')
    context.exit(1)


def pelican(config, *extra_params, production=False):
    os.makedirs(config['OUTPUT_DIR'], exist_ok=True)

    command = 'pelican "{content}" --output="{output}" --settings="{settings}"'
    if extra_params:
        command = ' '.join([command] + list(extra_params))

    command = command.format(
        content=config['CONTENT_DIR'],
        output=config['OUTPUT_DIR'],
        settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
    )
    run(command, env={'PRODUCTION': '1'} if production else None)
