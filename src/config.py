import os
import yaml


def get_config(*args):
    """
    Get configuration

    Takes path separated by comma
    """
    dirname = os.path.dirname(__file__)
    conf_filename = os.path.join(dirname, '../config.yaml')
    config = yaml.safe_load(open(conf_filename, 'r'))

    data = config
    for key in args:
        data = data.get(key)

    return data


def get_logger_config():
    """
    Get logger configuration
    """
    dirname = os.path.dirname(__file__)
    conf_filename = os.path.join(dirname, '../logger.yaml')
    config = yaml.safe_load(open(conf_filename, 'r'))

    return config
