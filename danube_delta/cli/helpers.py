
import os
import sys
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


def run(command, format=None, env=None, redir=False, redir_hook=None,
        bg=False):
    if format:
        command = command.format(**format)

    options = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.STDOUT,
        'bufsize': 1,
        'universal_newlines': True,
        'env': dict(os.environ, **env) if env else os.environ,
    }

    if bg:
        return subprocess.Popen(shlex.split(command), **options)

    with subprocess.Popen(shlex.split(command), **options) as proc:
        if redir:
            click.secho(command, fg='cyan', err=True)
            for line in iter(proc.stdout.readline, ''):
                print('r')
                # if redir_hook:
                #     line = redir_hook(line)
                # if line is not None:
                sys.stdout.write(line)

        print('end')
        stdout = proc.communicate()[0].strip()
        retcode = proc.poll()
        if retcode:
            raise subprocess.CalledProcessError(retcode, proc.args,
                                                output=stdout, stderr='')
        return stdout


def header(text):
    click.secho(text, fg='yellow')


def abort(context):
    click.echo('Aborted!')
    context.exit(1)
