"""configure"""
import os

import yaml


class Configure:
    def __init__(self):
        self.curr_path = os.path.dirname(__file__)
        config_name = 'application.yml'
        with open(self.curr_path + f'/{config_name}', 'r', encoding='utf-8') as f:
            self.conf = yaml.full_load(f)


config = Configure().conf
