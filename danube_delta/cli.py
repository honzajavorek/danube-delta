
import os
import re
import sys
import random
import shutil
import requests
import contextlib
from glob import glob
import importlib.util
from datetime import datetime

import click
from slugify import slugify
from PIL import Image, ImageFilter
from pelican.settings import DEFAULT_CONFIG
from sh import git, ghp_import, pelican, python, ErrorReturnCode, flake8


IMAGE_MAX_SIZE = 1900
IMAGE_SAVE_OPTIONS = {
    'quality': 100,
    'optimize': True,
    'progressive': True,
}
IMAGES_PATH = 'images'

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
@click.pass_context
def write(context):
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
    click.launch(path)


@blog.command(help='Adds images from given path to your last article')
@click.argument('path')
@click.pass_context
def photos(context, path):
    config = context.obj

    article_filename = find_last_article(config['CONTENT_DIR'])
    if not article_filename:
        return click.echo('No articles.')

    images = list(find_images(path))
    if not images:
        return click.echo('Found no images.')

    for filename in images:
        click.secho(filename, fg='yellow')

    if not click.confirm('\nAdd these images to your last article'):
        click.echo('Aborted!')
        context.exit(1)

    url_prefix = os.path.join('{filename}', IMAGES_PATH)
    images_dir = os.path.join(config['CONTENT_DIR'], IMAGES_PATH)
    os.makedirs(images_dir, exist_ok=True)

    urls = []
    for filename in images:
        image_basename = os.path.basename(filename).lower()
        urls.append(os.path.join(url_prefix, image_basename))
        image_filename = os.path.join(images_dir, image_basename)

        if os.path.isfile(image_filename):
            click.echo('Already exists, skipping: {}'.format(image_filename))
        else:
            image = Image.open(filename)
            image.thumbnail((IMAGE_MAX_SIZE, IMAGE_MAX_SIZE))
            image.filter(ImageFilter.SHARPEN)
            click.echo('Saving: {}'.format(image_filename))
            image.save(image_filename, image.format, **IMAGE_SAVE_OPTIONS)

    content = '\n'
    for url in urls:
        content += '\n![image description]({})\n'.format(url)

    click.echo('Adding to article: {}'.format(article_filename))
    with click.open_file(article_filename, 'a') as f:
        f.write(content)
    click.launch(article_filename)


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


@blog.command(help='Looks for errors in source code of your blog')
@click.pass_context
def lint(context):
    try:
        flake8('.', exclude='env', **redirect_output())
    except ErrorReturnCode:
        context.exit(1)


@blog.command(help='Saves changes and sends them to GitHub')
@click.pass_context
def publish(context):
    if get_branch() != 'master':
        click.echo("Your current Git branch is '{}' instead of master.".format(current_branch))
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
        git.commit(m='Publishing {}'.format(random.choice(COMMIT_EMOJIS)))
    else:
        click.echo('No changes.')

    click.echo('Pushing to GitHub...')
    git.push('origin', 'master', **redirect_output())

    pr_link = get_pr_link()
    if pr_link:
        click.launch(pr_link)


@blog.command(help="Updates your blog with other people's changes from GitHub")
def update():
    git.pull('origin', 'master', **redirect_output())


@blog.command(help='Uploads new version of your public blog website')
@click.pass_context
def deploy(context):
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
        'authors.html', 'categories.html',
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
    commit_message = 'Deploying {}'.format(random.choice(COMMIT_EMOJIS))
    ghp_import('-m', commit_message, config['OUTPUT_DIR'])

    click.echo('Pushing to GitHub...')
    git.push('origin', 'gh-pages', force=True)


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


def find_files(path):
    if os.path.isdir(path):
        for root_path, dir_paths, file_paths in os.walk(path):
            yield root_path
            for dir_path in dir_paths:
                yield os.path.join(root_path, dir_path)
            for file_path in file_paths:
                yield os.path.join(root_path, file_path)
    else:
        yield path


def find_images(path):
    for filename in find_files(path):
        try:
            Image.open(filename)
        except IOError:
            continue
        else:
            yield filename


def find_last_article(content_dir):
    articles = list(sorted(glob(os.path.join(content_dir, '*.md'))))
    if not articles:
        return None

    filename = articles[-1]
    date = os.path.basename(filename)[0:10]

    candidates = []
    for filename in articles:
        if os.path.basename(filename)[0:10] == date:
            candidates.append(filename)

    if len(candidates) == 1:
        return candidates[0]

    to_sort = []
    for filename in candidates:
        with click.open_file(filename) as f:
            match = re.search(r'Date: (.+)', f.read())
        creation_date = match.group(1)
        to_sort.append((creation_date, filename))

    return list(sorted(to_sort))[-1][1]


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
