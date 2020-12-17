import inspect
import pathlib

import click

HELP_STRING = """
generate debug environment into .env file.

    Run `source .env` to get commands.

\b
You can find argument {deploy-id} in slack notification. eg:
============ Slack Notification ======================
argo workflow
tpctl-hello-test-tpctl-q948q
^^^ {DEPLOY ID} ^^^^^^^^^^^^
=======================================================
"""


def generate_script(deploy_id):
    variables = inspect.cleandoc("""
    DEPLOY_ID={}
    """.format(deploy_id))

    with open(pathlib.Path(__file__).parent.absolute() / './scripts/env_raw.sh', 'rt') as f:
        functions = ''.join(f.readlines())
    return variables + '\n' + functions


def print_debug_help():
    click.echo(
        'Generate .env in current directory\n' +
        'Run to get debug commands:\n' +
        click.style('source .env', fg='green')
    )


@click.command(help=HELP_STRING)
@click.argument('deploy-id')
def debug(**params):
    """
    Dependency: argo and kubectl are installed and properly configured in current machine.
    """
    deploy_id = params['deploy_id']

    with open(".env", 'wt') as f:
        f.write(generate_script(
            deploy_id=deploy_id
        ))
    print_debug_help()
