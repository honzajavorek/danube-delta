
from sh import git, pip

from . import blog
from .helpers import redirect_output


@blog.command()
def update():
    """Gets other people's changes from GitHub"""

    git.pull('origin', 'master', **redirect_output())
    pip.install(r='./requirements.txt', upgrade=True, **redirect_output())
