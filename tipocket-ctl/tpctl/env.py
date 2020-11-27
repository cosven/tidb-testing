import os
import sys

import click


class Env:
    def __init__(self):
        self.dir_root = 'tpctl-build'
        self.dir_bin =  os.path.join(self.dir_root, 'bin')
        self.dir_config = os.path.join(self.dir_root, 'config')

    def ensure_preconditions(self):
        pwd = os.getcwd()
        if os.path.split(pwd)[-1] != 'tipocket':
            click.secho('you must run this command in tipocket root directory', fg='red')
            sys.exit(1)

        def mkdir_p(dir):
            if not os.path.exists(dir):
                os.mkdir(dir)

        mkdir_p(self.dir_root)
        mkdir_p(self.dir_bin)
        mkdir_p(self.dir_config)
