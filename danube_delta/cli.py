
import os
import re
import sys
import random
import shutil
import importlib.util
from datetime import datetime

import sh
import click
from slugify import slugify
from pelican.settings import DEFAULT_CONFIG


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


@click.group()
@click.version_option()
@click.pass_context
def blog(context):
    cwd = os.getcwd()

    settings_path = 'settings.py'
    settings_file = os.path.join(cwd, settings_path)

    config = {'CWD': cwd, 'SETTINGS_PATH': settings_path}
    config.update(DEFAULT_CONFIG)
    config.update(load_settings_file_as_dict(settings_file))

    config['CONTENT_DIR'] = os.path.join(cwd, config['PATH'])
    config['OUTPUT_DIR'] = os.path.join(cwd, config['OUTPUT_PATH'])

    context.obj = config


@blog.command(help='Starts a new article')
@click.option('--open/--no-open', default=True, help='Open in editor')
@click.pass_context
def write(context, open):
    config = context.obj

    title = click.prompt('Title')
    author = click.prompt('Author', default=config.get('DEFAULT_AUTHOR'))

    slug = slugify(title)
    creation_date = datetime.now()
    basename = '{:%Y-%m-%d}_{}.md'.format(creation_date, slug)
    meta = (
        ('Title', title),
        ('Date', '{:%Y-%m-%d %H:%M}:00'.format(creation_date)),
        ('Modified', '{:%Y-%m-%d %H:%M}:00'.format(creation_date)),
        ('Author', author),
    )

    file_content = ''
    for key, value in meta:
        file_content += '{}: {}\n'.format(key, value)
    file_content += '\n\n'
    file_content += 'Text...\n\n'
    file_content += '![image description]({filename}/images/my-photo.jpg)\n\n'
    file_content += 'Text...\n\n'

    os.makedirs(config['CONTENT_DIR'], exist_ok=True)
    path = os.path.join(config['CONTENT_DIR'], basename)
    with click.open_file(path, 'w') as f:
        f.write(file_content)

    click.echo(path)
    if open:
        click.launch(path)


@blog.command(help='Opens local preview of your blog website')
@click.pass_context
def preview(context):
    config = context.obj
    state = {'ready': False}

    def open_browser(line):
        if not state['ready'] and line.startswith('Done: Processed'):
            state['ready'] = True
            click.launch('http://localhost:8000')
        return line

    server = None
    pelican = None

    os.chdir(config['OUTPUT_DIR'])
    try:
        server = sh.python(
            '-m', 'http.server', '8000',
            _bg=True,
        )
        pelican = sh.pelican(
            config['CONTENT_DIR'],
            output=config['OUTPUT_DIR'],
            settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
            autoreload=True, debug=True, ignore_cache=True,
            _bg=True, **redirect_output(open_browser)
        )
        server.wait()
        pelican.wait()

    except:
        if server is not None:
            server.process.kill()
        if pelican is not None:
            pelican.process.kill()
        raise


@blog.command(help='Looks for errors in source code of your blog')
@click.pass_context
def lint(context):
    try:
        sh.flake8('.', exclude='env', **redirect_output())
    except sh.ErrorReturnCode:
        context.exit(1)


@blog.command(help='Saves changes and sends them to GitHub')
@click.pass_context
def publish(context):
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
            click.echo(' · {}'.format(click.style(path, fg='yellow')))

        if other_changes:
            click.echo('\nSome changes not related to content of the blog:\n')
            for path in other_changes:
                click.echo(' · {}'.format(click.style(path, fg='blue')))
            click.echo('\nYou will have to save those manually.')

        if not click.confirm('\nContinue publishing'):
            click.echo('Aborted!')
            context.exit(1)

        for path in content_changes:
            if os.path.isfile(path) and os.path.splitext(path)[1] == '.md':
                click.echo('Updating modification date: {}'.format(path))
                update_modified(path)

        sh.git.add('content', A=True)
        sh.git.commit(m='Publishing {}'.format(random.choice(COMMIT_EMOJIS)))
    else:
        click.echo('No changes.')

    click.echo('Pushing to GitHub...')
    sh.git.push('origin', 'master', **redirect_output())


@blog.command(help='Uploads new version of your public blog website')
@click.pass_context
def deploy(context):
    config = context.obj

    click.echo('Generating HTML...')
    sh.pelican(
        config['CONTENT_DIR'],
        output=config['OUTPUT_DIR'],
        settings=os.path.join(config['CWD'], config['SETTINGS_PATH']),
        _env={'PRODUCTION': '1'},
        **redirect_output()
    )

    click.echo('Removing unnecessary output...')
    unnecessary_paths = [
        'author', 'category', 'drafts', 'tag', 'feeds', 'tags.html',
        'authors.html', 'categories.html',
    ]
    for path in unnecessary_paths:
        remove_path(os.path.join(config['OUTPUT_DIR'], path))

    if os.environ.get('TRAVIS'):  # Travis CI
        click.echo('Setting up Git...')
        sh.git.config('user.name', sh.git('show', format='%cN', s=True))
        sh.git.config('user.email', sh.git('show', format='%cE', s=True))

        github_token = os.environ.get('GITHUB_TOKEN')
        repo_slug = os.environ.get('TRAVIS_REPO_SLUG')
        origin = 'https://{}@github.com/{}.git'.format(github_token, repo_slug)
        sh.git.remote('set-url', 'origin', origin)

    click.echo('Rewriting gh-pages branch...')
    commit_message = 'Deploying {}'.format(random.choice(COMMIT_EMOJIS))
    sh.ghp_import('-m', commit_message, config['OUTPUT_DIR'])

    click.echo('Pushing to GitHub...')
    sh.git.push('origin', 'gh-pages', force=True)

    click.echo('Done!')


def load_settings_file_as_dict(filename):
    file_spec = importlib.util.spec_from_file_location('settings', filename)
    module = importlib.util.module_from_spec(file_spec)
    file_spec.loader.exec_module(module)

    config = {}
    for (key, value) in module.__dict__.items():
        if key.upper() == key:
            config[key] = value
    return config


def remove_path(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, ignore_errors=True)


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
    for line in sh.git('status', porcelain=True):
        match = re.match(r'\s*\S+ (.+)', str(line))
        path = match.group(1)

        if os.path.isdir(path):
            for root_path, dir_paths, file_paths in os.walk(path):
                yield root_path
                for dir_path in dir_paths:
                    yield os.path.join(root_path, dir_path)
                for file_path in file_paths:
                    yield os.path.join(root_path, file_path)
        else:
            yield path


def redirect_output(filter_fn=None):
    def redirect_stdout(line, stdin, process):
        if filter_fn:
            line = filter_fn(line)
        sys.stdout.write(line)

    def redirect_stderr(line, stdin, process):
        if filter_fn:
            line = filter_fn(line)
        sys.stderr.write(line)

    return {'_out': redirect_stdout, '_err': redirect_stderr}
