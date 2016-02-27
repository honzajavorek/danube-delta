
import click
from sh import flake8, ErrorReturnCode

from . import blog
from .helpers import redirect_output


@blog.command()
@click.pass_context
def lint(context):
    """Looks for errors in source code of your blog"""

    try:
        flake8('.', exclude='env', **redirect_output())
    except ErrorReturnCode:
        context.exit(1)
