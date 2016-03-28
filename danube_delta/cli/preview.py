
import os
import sys

import click

from . import blog
from .helpers import run


PORT = 8000


@blog.command()
@click.pass_context
def preview(context):
    """Opens local preview of your blog website"""

    config = context.obj

    # raise NotImplementedError()
    #
    #
    # command = (
    #     'pelican "{content}" --output="{output}" --settings="{settings}" '
    #     '--autoreload --verbose --ignore-cache'
    # ).format(**{
    #     'content': config['CONTENT_DIR'],
    #     'output': config['OUTPUT_DIR'],
    #     'settings': os.path.join(config['CWD'], config['SETTINGS_PATH']),
    # })
    # import subprocess, shlex
    # subprocess.run(shlex.split(command))
    #
    #
    # state = {'ready': False}
    #
    # def open_browser(line):
    #     if not state['ready'] and line.startswith('Done: Processed'):
    #         state['ready'] = True
    #         click.launch('http://localhost:8000')
    #     return line
    #
    # server_proc = None
    # os.chdir(config['OUTPUT_DIR'])
    # try:
    #     command = 'python -m http.server ' + str(PORT)
    #     server_proc = run(command, bg=True)
    #
    #     command = (
    #         'pelican "{content}" --output="{output}" '
    #         ' --settings="{settings}" --autoreload --verbose --ignore-cache'
    #     )
    #     run(command, format={
    #         'content': config['CONTENT_DIR'],
    #         'output': config['OUTPUT_DIR'],
    #         'settings': os.path.join(config['CWD'], config['SETTINGS_PATH']),
    #     }, redir=True, redir_hook=open_browser)
    #
    # except:
    #     if server_proc is not None:
    #         server_proc.kill()
    #     raise
