
import re
import contextlib

from lxml import html


@contextlib.contextmanager
def modify_html(article):
    content = article._content
    html_tree = html.fromstring(content)

    yield html_tree

    content = html.tostring(html_tree, encoding='unicode')
    content = re.sub(r'%7B(\w+)%7D', r'{\1}', content)
    content = re.sub(r'%7C(\w+)%7C', r'|\1|', content)
    article._content = content


def wrap_element(element, wrapper_element):
    element.addprevious(wrapper_element)
    wrapper_element.insert(0, element)
    return wrapper_element
