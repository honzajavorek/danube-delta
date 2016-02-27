
import os

import click
from sh import python, pelican

from . import blog
from .helpers import redirect_output


@blog.command()
@click.pass_context
def preview(context):
    """Opens local preview of your blog website"""

    config = context.obj
    state = {'ready': False}

    def open_browser(line):
        if not state['ready'] and line.startswith('Done: Processed'):
            state['ready'] = True
            click.launch('http://localhost:8000')
        return line

    server_cmd = None
    pelican_cmd = None

    os.chdir(config['OUTPUT_DIR'])
    try:
        server_cmd = python(
            '-m', 'http.server', '8000',
            _bg=True,
        )
        pelican_cmd = pelican(
            config['CONTENT_DIR'],
            output=config['OUTPUT_DIR'],
            settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
            autoreload=True, debug=True, ignore_cache=True,
            _bg=True, **redirect_output(open_browser)
        )
        server_cmd.wait()
        pelican_cmd.wait()

    except:
        if server_cmd is not None:
            server_cmd.process.kill()
        if pelican_cmd is not None:
            pelican_cmd.process.kill()
        raise
