import os

import yaml

_dirname = os.path.dirname(__file__)
_conf_filename = os.path.join(_dirname, '../config.yaml')
_config = yaml.safe_load(open(_conf_filename, 'r'))


def get_config(*args):
    """
    Takes path separated by comma
    """
    data = _config
    for key in args:
        data = data.get(key)

    return data