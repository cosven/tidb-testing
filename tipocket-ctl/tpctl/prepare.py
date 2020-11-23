import os
import sys
from functools import wraps

import click
import yaml
from click_option_group import optgroup

from tpctl.app import cli
from tpctl.build import Build
from tpctl.case import Case
from tpctl.deploy import Deploy
from tpctl.env import Env
from tpctl.tidb_cluster import ComponentName


# RESOURCES_DIR = 'tpctl-build/resources'
COMPONENTS = ['tikv', 'tidb', 'pd']

COMMON_OPTIONS = (
    optgroup.group('Test case build options'),
    optgroup.option('--build-image/--no-build-image', default=False),
    # *[optgroup.option(f'--use-tpctl-{component}-config', is_flag=True, default=False)
    #   for component in COMPONENTS],

    optgroup.group('Test case common options'),
    optgroup.option('--client', default='5'),
    optgroup.option('--run-time', default='10m'),
    optgroup.option('--nemesis', default=''),
    optgroup.option('--purge/--no-purge', default=False),

    optgroup.group('TiDB cluster options'),
    optgroup.option('--namespace', default=''),
    optgroup.option('--hub', default='docker.io'),
    optgroup.option('--repository', default='pingcap'),
    optgroup.option('--image-version', default='nightly'),
    *[optgroup.option(f'--{component}-image', default='')
      for component in COMPONENTS],
    *[optgroup.option(f'--{component}-config', default='', type=click.Path())
      for component in COMPONENTS],
    optgroup.option('--tikv-replicas', default='5'),
    optgroup.option('--tidb-replicas', default='1'),
    optgroup.option('--pd-replicas', default='1'),

    optgroup.group('K8s options',
                   help='different K8s cluster has different values'),
    optgroup.option('--storage-class', default='local-storage',
                    show_default=True),

    optgroup.group('Test case logging options',
                   help='usually, you need not to change this'),
    optgroup.option('--loki-addr', default='http://gateway.loki.svc'),
    optgroup.option('--loki-username', default='loki'),
    optgroup.option('--loki-password', default='admin'),
)


def testcase_common_options(func):
    for option in reversed(COMMON_OPTIONS):
        func = option(func)
    return func


def testcase(binary, name, maintainers):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **params):
            click.echo('---pre')
            env = Env()
            click.echo(f'Ensure pwd is tipocket directory...')
            click.echo(f'Ensure workspace directory: ./{env.dir_root}...')
            env.ensure_preconditions()

            # build case
            click.echo('---build')
            build_image = params['build_image']
            config_filepaths = []
            for component in ComponentName.list_names():
                config_filepath = params[f'{component}_config']
                if config_filepath:
                    config_filepaths.append(config_filepath)
            build = Build(env, binary, build_image, config_filepaths)
            build.prepare()
            image = build.get_image()
            build_cmds = build.get_howto_cmds()

            if build_cmds:
                click.echo('Run following commands to rebuild the case')
                for cmd in build_cmds:
                    click.secho(cmd, fg='green')

            # deploy case
            click.echo('---deploy')
            case = Case(name, maintainers)
            deploy = Deploy(env, case, binary, image, params)
            deploy.prepare()
            deploy_cmds = deploy.get_howto_cmds()

            if deploy_cmds:
                click.echo('Run following commands to deploy the case')
                for cmd in deploy_cmds:
                    click.secho(cmd, fg='green')

            return func(*args, **params)
        return wrapper
    return deco


@click.group(help='generate configurations for running test cases')
def prepare():
    pass


@prepare.command()
@click.option('--accounts', default='1000000')
@click.option('--concurrency', default='200')
@click.option('--tidb-replica-read', default='leader')
@testcase_common_options
@testcase('bank2', 'scbank2', ['@yinshaowen'])
def scbank2(**params):
    """
    sc_bank2
    """


@prepare.command()
@click.option('--strict', default='true')
@click.option('--contenders', default='1')
@testcase_common_options
@testcase('pipelined-locking', 'pipelined-locking', ['@yinshaowen', '@zhaolei'])
def pipelined_locking(**params):
    """
    piplined pessimistic locking
    """
