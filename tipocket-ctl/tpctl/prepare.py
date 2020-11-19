import os
import sys
from functools import wraps

import click
import yaml
from click_option_group import optgroup

from tpctl.app import cli
from tpctl.argo import ArgoCase
from tpctl.case import Case, CaseInstance
from tpctl.dockerfile import local_dockerfile


BUILD_DIR = 'tpctl-build'
BIN_DIR = 'tpctl-build/bin'
CONFIG_DIR = 'tpctl-build/config'
# RESOURCES_DIR = 'tpctl-build/resources'
COMPONENTS = ['tikv', 'tidb', 'pd']

COMMON_OPTIONS = (
    optgroup.group('Test case build options'),
    optgroup.option('--build-image/--no-build-image', default=False),
    # *[optgroup.option(f'--use-tpctl-{component}-config', is_flag=True, default=False)
    #   for component in COMPONENTS],

    optgroup.group('Test case common options'),
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


def ensure_preconditions():
    pwd = os.getcwd()
    if os.path.split(pwd)[-1] != 'tipocket':
        click.secho('you must run this command in tipocket root directory', fg='red')
        sys.exit(1)

    def mkdir_p(dir):
        if not os.path.exists(dir):
            os.mkdir(dir)

    mkdir_p(BUILD_DIR)
    mkdir_p(BIN_DIR)
    mkdir_p(CONFIG_DIR)
    # mkdir_p(RESOURCES_DIR)


def parse_params(params):

    # convert parameters to the format that tipocket test case recognize
    case_params = {}
    for key, value in params.items():
        if key in ['build_image']:
            continue
        if key == 'purge':
            if value is True:
                value = 'true'
            else:
                value = 'false'
        if key.endswith('-config'):
            if value:
                value = '/' + value
        case_params[key.replace('_', '-')] = value

    return case_params, params


def testcase(binary, name, maintainers):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **params):
            click.echo(f'Ensure pwd is tipocket directory...')
            click.echo(f'Ensure build directory: ./{BUILD_DIR}...')
            ensure_preconditions()
            case_params, params = parse_params(params)
            build_image = params['build_image']

            namespace = case_params['namespace']
            if not namespace:
                namespace = f'tpctl-{name}'
                case_params['namespace'] = namespace

            if build_image:
                dockerfile = f'{BUILD_DIR}/tpctl-dockerfile'
                with open(dockerfile, 'w') as f:
                    f.write(local_dockerfile)
                image = f'hub.pingcap.net/tpctl/tipocket:{name}'
            else:
                image = 'pingcap/tipocket:latest'

            case = Case(name, binary, maintainers)
            case_inst = CaseInstance(case, case_params)
            argo_case = ArgoCase(case_inst, image, notify=True, notify_users=['@yinshaowen'])
            argo_workflow_filepath = f'{BUILD_DIR}/{name}.yaml'
            click.echo(f'Generating argo workflow {argo_workflow_filepath}...')
            with open(argo_workflow_filepath, 'w') as f:
                workflow_dict = argo_case.gen_workflow()
                yaml.dump(workflow_dict, f)

            # generate cmds for running test case
            cmds = []
            if build_image:
                for component in COMPONENTS:
                    config_file = params[f'{component}_config']
                    if config_file:
                        cmds.append(f'cp {config_file} {CONFIG_DIR}/')
                cmds.append(f'make {binary}')
                cmds.append(f'cp bin/{binary} {BIN_DIR}/')
                cmds.append(f'docker build {BUILD_DIR}/'
                            f' -f {BUILD_DIR}/tpctl-dockerfile'
                            f' -t {image}')
                cmds.append(f'')
                cmds.append(f'docker push {image}')
            cmds.append(f'argo submit {argo_workflow_filepath}')
            if cmds:
                click.echo('')
                click.echo('--------------------')
                click.secho(f'You can run {name} with following commands:')
                click.echo()
                click.secho('\n'.join(cmds), fg='green')

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
@testcase_common_options
@testcase('pipelined-locking', 'pipelined-locking', ['@yinshaowen'])
def pipelined_locking(**params):
    """
    piplined pessimistic locking
    """
