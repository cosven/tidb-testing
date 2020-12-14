import base64

import yaml

from tpctl.case import CaseInstance
from tpctl.yaml_dump_tidbcluster import dump


class ArgoCase:
    def __init__(self, feature, case: CaseInstance, image, tidb_cluster,
                 deploy_id="", notify=False, notify_users=None):
        # case metadata and build info
        self.feature = feature
        self.case = case
        self.image = image

        # to name argo workflow and namespace
        self.deploy_id = deploy_id

        # resources info
        self.tidb_cluster = tidb_cluster

        # notification
        self.notify = notify
        self.notify_users = notify_users

    def gen_workflow(self):
        case = self.case
        main_steps = []
        on_exit_steps = []
        if self.notify:
            users = self.notify_users or case.meta.maintainers
            if users:
                notify_step = self.gen_notify_step('notify-start', 'running')
                main_steps.append([notify_step])

                notify_failed_step = self.gen_notify_step(
                    'notify-end-failed', 'end', 'failed', r'{{workflow.status}} != Succeeded')
                notify_passed_step = self.gen_notify_step(
                    'notify-end-passed', 'end', 'passed', r'{{workflow.status}} == Succeeded')
                on_exit_steps.append([notify_failed_step, notify_passed_step])
        else:
            users = []
        main_steps.append([self.gen_case_step()])
        workflow = {
            'metadata': {
                'generateName': self.deploy_id + '-',
                'namespace': 'argo',
            },
            'spec': {
                'entrypoint': 'main',
                'onExit': 'on-exit',
                'templates': [
                    {'name': 'main', 'steps': main_steps},
                    {'name': 'on-exit', 'steps': on_exit_steps},
                    *([self.gen_notify_template(users)] if users else []),
                    self.gen_case_template(),
                ],
            },
        }
        return workflow

    def gen_case_step(self):
        case = self.case
        step = {
            'name': f'{case.meta.name}',
            'template': self._get_case_template_name(),
        }
        return step

    def gen_notify_step(self, name, stage, status='passed', when=None):
        step = {
            'name': f'{name}',
            'template': 'notify',
            'arguments': {
                'parameters': [
                    {'name': 'stage', 'value': stage},
                    {'name': 'status', 'value': status},
                ]
            },
        }
        if when is not None:
            step['when'] = when
        return step

    def gen_notify_template(self, users):
        def encode(s):
            return base64.b64encode(bytes(s, 'utf-8')).decode('utf-8')

        encoded_cmd = encode(self.case.get_cmd())
        encoded_tidbcluster = encode(dump(self.tidb_cluster.to_json()))
        return {
            'name': 'notify',
            'inputs': {
                'parameters': [
                    {'name': 'stage'},
                    {'name': 'status', 'default': 'passed'},
                ]
            },
            'container': {
                'name': 'notify-py',
                'image': 'hub.pingcap.net/tpctl/notify',
                'imagePullpolicy': 'Always',
                'args': [
                    ','.join(users),
                    self.case.meta.name,
                    r'{{workflow.name}}',
                    r'{{inputs.parameters.stage}}',
                    '--status',
                    r'{{inputs.parameters.status}}',
                    '--cmd',
                    f'{encoded_cmd}',
                    '--tidbcluster',
                    f'{encoded_tidbcluster}',
                ],
                'env': [
                    {
                        'name': 'SLACK_BOT_TOKEN',
                        'valueFrom': {
                            'secretKeyRef': {
                                'name': 'tipocket-slack-token',
                                'key': 'token'
                            }
                        }
                    }
                ]
            }
        }

    def gen_case_template(self):
        case = self.case
        return {
            'name': self._get_case_template_name(),
            # 'outputs': {
            #     'artifacts': [
            #         {
            #             'name': 'case-log',
            #             'archiveLogs': True,
            #             'path': '/var/run/tipocket-logs',
            #         },
            #     ]
            # },
            'metadata': {
                'labels': {
                    'ns': case.params['namespace'],
                }
            },
            'container': {
                'name': case.meta.name,
                'image': self.image,
                'imagePullpolicy': 'Always',
                'command': ['sh', '-c', case.get_cmd()]
            }
        }

    def _get_case_template_name(self):
        return self.case.meta.name


class ArgoCronCase(ArgoCase):
    def __init__(self, feature, case: CaseInstance, image, tidb_cluster,
                 deploy_id="", notify=False, notify_users=None, cron_params=None):
        super().__init__(feature, case, image, tidb_cluster,
                         deploy_id, notify, notify_users)
        self.cron_params = cron_params

    def gen_workflow(self):
        workflow = super().gen_workflow()
        # use fixed name for cron workflow
        metadata = workflow['metadata']
        metadata.pop('generateName')
        metadata['name'] = self.deploy_id
        workflow['kind'] = 'CronWorkflow'
        workflow['spec'] = {'workflowSpec': workflow['spec']}
        for k, v in self.cron_params.items():
            workflow['spec'][k] = v
        return workflow
