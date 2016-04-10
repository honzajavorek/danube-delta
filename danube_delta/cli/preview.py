
import os
import time

import click

from . import blog
from .helpers import run, abort, pelican


PORT = 8000


@blog.command()
@click.pass_context
def preview(context):
    """Opens local preview of your blog website"""

    config = context.obj

    server_proc = None
    os.chdir(config['OUTPUT_DIR'])

    pelican(config, '--verbose', '--ignore-cache')
    try:
        try:
            command = 'python -m http.server ' + str(PORT)
            server_proc = run(command, bg=True)

            time.sleep(3)
            click.launch('http://localhost:8000')

            pelican(config, '--autoreload')
        except:
            if server_proc is not None:
                server_proc.kill()
            raise
    except KeyboardInterrupt:
        abort(context)
