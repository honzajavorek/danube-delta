import os
import shutil

import click

from . import blog
from .helpers import choose_commit_emoji, run, header, pelican


@blog.command()
@click.pass_context
def deploy(context):
    """Uploads new version of the blog website"""

    config = context.obj

    header('Generating HTML...')
    pelican(config, '--verbose', production=True)

    header('Removing unnecessary output...')
    unnecessary_paths = [
        'author', 'category', 'tag', 'feeds', 'tags.html',
        'authors.html', 'categories.html', 'archives.html',
    ]
    for path in unnecessary_paths:
        remove_path(os.path.join(config['OUTPUT_DIR'], path))

    if os.environ.get('TRAVIS'):  # Travis CI
        header('Setting up Git...')
        run(
            'git config user.name ' +
            run('git show --format="%cN" -s', capture=True)
        )
        run(
            'git config user.email ' +
            run('git show --format="%cE" -s', capture=True)
        )

        github_token = os.environ.get('GITHUB_TOKEN')
        repo_slug = os.environ.get('TRAVIS_REPO_SLUG')
        origin = 'https://{}@github.com/{}.git'.format(github_token, repo_slug)
        run('git remote set-url origin ' + origin)

    header('Rewriting gh-pages branch...')
    run('ghp-import -m "{message}" {dir}'.format(
        message='Deploying {}'.format(choose_commit_emoji()),
        dir=config['OUTPUT_DIR'],
    ))

    header('Pushing to GitHub...')
    run('git push origin gh-pages:gh-pages --force')


def remove_path(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, ignore_errors=True)
