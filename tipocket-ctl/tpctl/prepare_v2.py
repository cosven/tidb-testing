import click

from .prepare import testcase_common_options
from .case import Case
from .deploy import Deploy
from .env import Env


@click.command()
@click.argument('--', nargs=-1, type=click.UNPROCESSED)
@testcase_common_options
def prepare_v2(**params):
    case_cmd_args = params['--']
    assert case_cmd_args.startswith('bin/')

    # parse case metadata
    binary_path, _ = case_cmd_args.split(' ', 1)
    binary = case_name = binary_path.split('/')[1]

    click.echo('---pre')
    env = Env()
    click.echo('Ensure pwd is tipocket directory...')
    click.echo(f'Ensure workspace directory: ./{env.dir_root}...')
    env.ensure_preconditions()

    case = Case(case_name, maintainers=[])
    Deploy(env, params['feature'], case, binary, params['image'], params)
