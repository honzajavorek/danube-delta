
import re
import os
from datetime import datetime

import click
import requests
from sh import git

from . import blog
from .helpers import choose_commit_emoji, redirect_output, find_files


@blog.command()
@click.pass_context
def publish(context):
    """Saves changes and sends them to GitHub"""

    branch = get_branch()
    if branch != 'master':
        click.echo("Your current Git branch is '{}' instead of master.".format(
                   branch))
        context.exit(1)

    content_changes = []
    other_changes = []

    content_re = re.compile(r'^content/')
    for path in get_changes():
        if content_re.match(path):
            content_changes.append(path)
        else:
            other_changes.append(path)

    if content_changes:
        click.echo('Changes to be published:\n')
        for path in content_changes:
            click.secho(path, fg='yellow')

        if other_changes:
            click.echo('\nSome changes are not related to content '
                       'of the blog:\n')
            for path in other_changes:
                click.secho(path, fg='blue')
            click.echo('\nYou will have to save those manually.')

        if not click.confirm('\nContinue publishing'):
            click.echo('Aborted!')
            context.exit(1)

        for path in content_changes:
            if os.path.isfile(path) and os.path.splitext(path)[1] == '.md':
                click.echo('Updating modification date: {}'.format(path))
                update_modified(path)

        git.add('content', A=True)
        git.commit(m='Publishing {}'.format(choose_commit_emoji()))
    else:
        click.echo('No changes.')

    click.echo('Pushing to GitHub...')
    git.push('origin', 'master', **redirect_output())

    pr_link = get_pr_link()
    if pr_link:
        click.launch(pr_link)


def update_modified(filename):
    modification_date = datetime.now()
    with click.open_file(filename) as f:
        article_src = f.read()
    article_src = re.sub(
        r'Modified: (.+)',
        'Modified: {:%Y-%m-%d %H:%M}:00'.format(modification_date),
        article_src,
    )
    with click.open_file(filename, 'w') as f:
        f.write(article_src)


def get_changes():
    for line in git('status', porcelain=True):
        match = re.match(r'\s*\S+ (.+)', str(line))
        path = match.group(1)
        yield from find_files(path)


def get_pr_link():
    repo_slug = get_repo_slug()
    repo_url = 'https://api.github.com/repos/{}'.format(repo_slug)

    res = requests.get(repo_url)
    res.raise_for_status()
    repo_info = res.json()

    if not repo_info['fork']:
        return None

    return 'https://github.com/{}/compare/master...{}:master'.format(
        repo_info['parent']['full_name'],
        repo_info['owner']['login']
    )


def get_repo_slug():
    url = str(git.remote('get-url', 'origin'))
    return re.search(r'github\.com[\:\/](.+)\.git$', url).group(1)


def get_branch():
    return re.search(r'\*\s+(\S+)', str(git.branch(no_color=True))).group(1)
