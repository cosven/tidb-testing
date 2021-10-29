import os
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


class DebugToolBox:
    """
    Prototype of a certain debug task.
    Use it to generate debug/ dir with commands in debug/.env
    """

    def __init__(self, deploy_id, case_namespace, debug_parent="/tmp/"):
        self.deploy_id = deploy_id
        self.case_namespace = case_namespace
        self.debug_parent = pathlib.Path(debug_parent)
        self.debug_dir = pathlib.Path(debug_parent) / deploy_id

    def generate_all(self):
        if not os.path.exists(self.debug_dir):
            os.mkdir(self.debug_dir)
        with open(pathlib.Path(self.debug_dir) / ".env", 'wt') as f:
            f.write(self.script())

    def script(self):
        variables = f'DEPLOY_ID={self.deploy_id}\nCASE_NAMESPACE={self.case_namespace}'
        with open(pathlib.Path(__file__).parent.absolute() / './scripts/env_raw.sh', 'rt') as f:
            functions = ''.join(f.readlines())
        return variables + '\n' + functions

    def print_help(self):
        click.echo(
            'Generate .env in {}\n'.format(self.debug_dir) +
            'Run to get debug commands:\n' +
            click.style('cd {}\n'.format(self.debug_dir), fg='green') +
            click.style('source .env', fg='green')
        )


@click.command(help=HELP_STRING)
@click.argument('deploy-id')
@click.option('--case-namespace', default='argo', help='Namespace of tipocket case itself. Default is `argo`.')
def debug(**params):
    """
    Dependency: argo and kubectl are installed and properly configured in current machine.
    """
    toolbox = DebugToolBox(
        deploy_id=params['deploy_id'],
        case_namespace=params['case_namespace']
    )
    toolbox.generate_all()
    toolbox.print_help()
