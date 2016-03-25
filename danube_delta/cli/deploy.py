
import os
import shutil

import click
from sh import git, pelican, ghp_import

from . import blog
from .helpers import redirect_output, choose_commit_emoji


@blog.command()
@click.pass_context
def deploy(context):
    """Uploads new version of the blog website"""

    config = context.obj

    click.echo('Generating HTML...')
    pelican(
        config['CONTENT_DIR'],
        output=config['OUTPUT_DIR'],
        settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
        _env={'PRODUCTION': '1'},
        **redirect_output()
    )

    click.echo('Removing unnecessary output...')
    unnecessary_paths = [
        'author', 'category', 'drafts', 'tag', 'feeds', 'tags.html',
        'authors.html', 'categories.html', 'archives.html',
    ]
    for path in unnecessary_paths:
        remove_path(os.path.join(config['OUTPUT_DIR'], path))

    if os.environ.get('TRAVIS'):  # Travis CI
        click.echo('Setting up Git...')
        git.config('user.name', git('show', format='%cN', s=True))
        git.config('user.email', git('show', format='%cE', s=True))

        github_token = os.environ.get('GITHUB_TOKEN')
        repo_slug = os.environ.get('TRAVIS_REPO_SLUG')
        origin = 'https://{}@github.com/{}.git'.format(github_token, repo_slug)
        git.remote('set-url', 'origin', origin)

    click.echo('Rewriting gh-pages branch...')
    commit_message = 'Deploying {}'.format(choose_commit_emoji())
    ghp_import('-m', commit_message, config['OUTPUT_DIR'])

    click.echo('Pushing to GitHub...')
    git.push('origin', 'gh-pages:gh-pages', force=True)


def remove_path(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, ignore_errors=True)
