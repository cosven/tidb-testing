import base64
import shlex
import sys

import click
import yaml
from click_option_group import optgroup

from tpctl.case import BinaryCase, ArgoCase
from tpctl.tidb_cluster import ComponentName, ComponentSpec, TidbClusterSpec


# RESOURCES_DIR = 'tpctl-build/resources'
COMPONENTS = ['tikv', 'tidb', 'pd']

# Those options won't be passed to tipocket case.
IGNORE_OPTION_LIST = [
    'image',
    'subscriber',
    'feature',
    'cron',
    'cron_schedule',
    'description',
]

# Those options would be passed to tipocket case,
# except those in IGNORE_OPTION_LIST.
COMMON_OPTIONS = (
    # !!! remember to update params.IGNORE_OPTION_LIST when
    # a parameter is modified
    optgroup.group('Test case deploy options'),
    optgroup.option('--subscriber', multiple=True),
    optgroup.option('--feature', default='universal'),
    optgroup.option('--image', default="hub.pingcap.net/qa/tipocket"),
    optgroup.option('--description', default=''),
    optgroup.option('--cron/--not-cron', default=False),
    optgroup.option('--cron-schedule', default='30 17 * * *'),

    optgroup.group('Test case common options'),
    optgroup.option('--prepare-sql', default=''),
    # HELP: We can add `failpoint.tidb` as option since click can't recognize
    # the option name when there is a dot.
    # optgroup.option('--failpoint.tidb', 'failpoint.tidb', default='',),
    optgroup.option('--round', default='1'),
    optgroup.option('--client', default='5'),
    optgroup.option('--run-time', default='10m'),
    optgroup.option('--wait-duration', default='10m'),
    optgroup.option('--nemesis', default=''),
    optgroup.option('--purge/--no-purge', default=True),
    optgroup.option('--delns/--no-delns', 'delNS', default=True),

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
    optgroup.option('--storage-class', default='local-path',
                    show_default=True),

    # optgroup.group('Test case logging options',
    #                help='usually, you need not to change this'),
    # set loki settings to empty since loki does not work well currently
    # optgroup.option('--loki-addr', default=''),  # http://gateway.loki.svc'
    # optgroup.option('--loki-username', default=''),  # loki
    # optgroup.option('--loki-password', default=''),  # admin
)


def testcase_common_options(func):
    for option in reversed(COMMON_OPTIONS):
        func = option(func)
    return func


def get_case_params(params):
    """
    validate params and generate params for test case
    """
    # convert parameters to the format that tipocket test case recognize
    case_params = {}
    for key, value in params.items():
        if key in IGNORE_OPTION_LIST:
            continue
        # convert True/False to 'true/false'
        if key in ('purge', 'delNS'):
            if value is True:
                value = 'true'
            else:
                value = 'false'
        if key.endswith('_config'):
            # value should be a valid config file path
            # TODO: catch FileNotExist error or validate the path somewhere
            if value:
                # read the content in config file and encode it with base64
                # https://github.com/pingcap/tipocket/pull/330
                with open(value) as f:
                    content = f.read()
                content_bytes = bytes(content, 'utf-8')
                b64content = base64.b64encode(content_bytes).decode('utf-8')
                value = f'base64://{b64content}'
        case_params[key.replace('_', '-')] = value
    return case_params


def get_tidb_cluster_spec_from_params(params):
    hub = params['hub']
    repository = params['repository']
    tag = params['image_version']

    components = []
    component_names = ComponentName.list_names()
    for component in component_names:
        config_path = params[f'{component}_config']
        # FIXME: the program must run in tipocket root directory
        if config_path:
            with open(config_path) as f:
                config = f.read()
        else:
            config = ''
        replicas = params[f'{component}_replicas']
        image = params[f'{component}_image']
        if not image:
            image = f'{hub}/{repository}/{component}:{tag}'
        component = ComponentSpec(component, image, replicas, config)
        components.append(component)
    return TidbClusterSpec.create_from_components(components)


@click.command(context_settings=dict(ignore_unknown_options=True))
@testcase_common_options
@click.argument('--', nargs=-1, required=True, type=click.UNPROCESSED)
def deploy(**params):
    """Deploy(debug/run) tipocket case on K8s

    \b
    Several usage examples:
    * tpctl deploy --subscriber '@slack_id' -- bin/bank2
    * tpctl deploy --image='myhub.io/tom/tipocket:case' --subscriber '@slack_id' -- bin/case -xxx
    * tpctl deploy --image='{your_tipocket_image}' --subscriber '@slack_id' -- bin/case -xxx
    * tpctl deploy --run-time='5m' --subscriber '@slack_id' -- bin/resolve-lock -enable-green-gc=false

    Note: case specific options(like `enable-green-gc`) should be followed
    by `--`, and the common options (like `run-time`) should be specified in
    command options.
    """
    case_cmd_args = params.pop('__')
    assert case_cmd_args and case_cmd_args[0].startswith('bin/')

    # Generate deploy id
    case_name = case_cmd_args[0].split('/')[1]
    is_cron = params['cron'] is True
    feature = params['feature']
    deploy_id = f'tpctl-{case_name}-{feature}'
    if is_cron:
        deploy_id += '-cron'
    click.echo(f'Case name is {click.style(case_name, fg="blue")}')
    # Generate case
    case_params = get_case_params(params)
    # Set namespace to deploy_id by default
    if not case_params['namespace']:
        case_params['namespace'] = deploy_id
    # Check case options
    for arg in case_cmd_args:
        if arg.startswith('-'):
            option_name = arg.split('=')[0][1:]
            if option_name not in case_params:
                continue
            click.secho(f"You should specify option '{option_name}' before --",
                        fg='red')
            sys.exit(1)
    # Input: tpctl deploy -- bin/cdc-bank -failpoint.tidb="set a=1"
    # Output: /bin/cdc-bank '-failpoint.tidb=set a=1' ...
    case_cmd = ' '.join(shlex.quote(arg) for arg in case_cmd_args)
    case_cmd = f'/{case_cmd}'
    for key, value in case_params.items():
        case_cmd += f' -{key}="{value}"'
    case = BinaryCase(case_name, case_cmd)
    click.echo('Generating command for running case...')
    click.secho(case_cmd, fg='blue')

    # generate argo workflow yaml
    argo_workflow_filepath = f'/tmp/{deploy_id}.yaml'
    image = params['image']
    tidb_cluster = get_tidb_cluster_spec_from_params(params)
    subscribers = params['subscriber'] or None
    argo_case = ArgoCase(deploy_id, case, image,
                         tidb_cluster,
                         description=params['description'],
                         notify_users=subscribers)
    click.echo(f'Generating argo workflow {click.style(argo_workflow_filepath, fg="blue")}...')
    with open(argo_workflow_filepath, 'w') as f:
        if is_cron:
            workflow_dict = argo_case.gen_cron_workflow({
                'schedule': params['cron_schedule'],
                'concurrencyPolicy': 'Forbid',
                'startingDeadlineSeconds': 0,
                'timezone': 'Asia/Shanghai',
            })
        else:
            workflow_dict = argo_case.gen_workflow()
        yaml.dump(workflow_dict, f)

    # show hints
    if is_cron:
        deploy_cmd = f'argo cron create {argo_workflow_filepath}'
    else:
        deploy_cmd = f'argo submit {argo_workflow_filepath}'
    click.echo('Run following commands to deploy the case')
    click.secho(deploy_cmd, fg='green')
