# -*- coding: utf-8 -*-

import os
import pkg_resources

import yaml

config_fname = pkg_resources.resource_filename(__name__, os.path.join('data', 'tech_params.yaml'))

with open(config_fname, 'r') as f:
    config = yaml.load(f)
