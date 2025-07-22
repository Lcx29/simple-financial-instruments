import os
from logging.config import dictConfig
from yaml import load, CLoader as Loader


def init_yml_log() -> None:
    log_config_file_path = os.path.abspath("") + "/log.yml"
    with open(log_config_file_path, mode='r') as obj:
        logging_config = load(obj, Loader=Loader)
    dictConfig(logging_config)
