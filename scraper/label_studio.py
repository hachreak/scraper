
"""Label studio utils."""

import os

from xml.etree import ElementTree as ET
from collections import defaultdict

from .utils import load_json


def _load_completion_filename(base_dir):
    """Load list of file completion names."""
    completion_names = os.listdir(base_dir)
    for name in completion_names:
        yield os.path.join(base_dir, name)


def _load_completions(base_dir):
    """Load all completions."""
    for filename in _load_completion_filename(base_dir):
        yield load_json(filename)


def _join_category_polarity(results, alias_to_label):
    """Create a single dictionary for category and polarity."""
    cp = defaultdict(dict)
    for r in results:
        id_ = r['id']
        from_name = r['from_name']
        # note: get only the first label because I can't label two times
        label = r['value']['labels'][0]
        # convert from_name + label -> value
        cp[id_][from_name] = alias_to_label(from_name, label)
        # get term (same for category and polarity)
        cp[id_]['term'] = r['value']['text']
    return cp


def _completion_to_asc(completion, alias_to_label):
    """Convert single completion file to ASC."""
    cid = completion['data']['comment_id']
    # note: get only first completion and skip other versions
    c = completion['completions'][0]
    # for each category / polarity
    for i, r in enumerate(_join_category_polarity(
            c['result'], alias_to_label).values()):
        id_ = ''.join([cid, '_', '{:04d}'.format(i)])
        r.update({
            'id': id_,
            'sentence': completion['data']['text'],
        })
        yield r


def alias_to_label(config_xml):
    """Load label alias lookup table from xml config file."""
    root = ET.parse(config_xml).getroot()
    lookup = defaultdict(dict)
    for label in root.findall('Labels'):
        for value in label.getchildren():
            v = value.get('value')
            name = label.get('name')
            alias = value.get('alias', v)
            lookup[name][alias] = v

    def f(name, alias):
        return lookup[name][alias]
    return f


def completitions_to_asc(base_dir, alias_to_label):
    """Convert a completion to ASC format."""
    for file_ in _load_completions(base_dir):
        for asc in _completion_to_asc(file_, alias_to_label):
            yield asc['id'], asc
