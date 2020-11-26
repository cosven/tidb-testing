import click
import yaml

from tpctl.argo import ArgoCase
from tpctl.case import Case, CaseInstance
from tpctl.params import parse_params, get_tidb_cluster_spec_from_params


class Deploy:
    def __init__(self, env, feature, case, binary, image, params):
        self._env = env
        self.feature = feature
        self.case = case
        self.binary = binary
        self.image = image
        self.params = params

        self._argo_workflow_filepath = \
            f'{env.dir_root}/{case.name}-{feature}.yaml'

    def prepare(self):
        case_params = parse_params(self.params)
        namespace = case_params['namespace']
        if not namespace:
            namespace = f'tpctl-{self.case.name}-{self.feature}'
            case_params['namespace'] = namespace
        case_inst = CaseInstance(self.case, self.binary, case_params)
        tidb_cluster = get_tidb_cluster_spec_from_params(self.params)
        subscribers = self.params['subscriber'] or None
        argo_case = ArgoCase(self.feature, case_inst, self.image, tidb_cluster,
                             notify=True, notify_users=subscribers)
        argo_workflow_filepath = self._argo_workflow_filepath
        click.echo(f'Generating argo workflow {argo_workflow_filepath}...')
        with open(argo_workflow_filepath, 'w') as f:
            workflow_dict = argo_case.gen_workflow()
            yaml.dump(workflow_dict, f)

    def get_howto_cmds(self):
        return [
            f'argo submit {self._argo_workflow_filepath}'
        ]
