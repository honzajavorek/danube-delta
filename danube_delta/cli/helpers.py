
import os
import sys
import random


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


def choose_commit_emoji():
    return random.choice(COMMIT_EMOJIS)


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
