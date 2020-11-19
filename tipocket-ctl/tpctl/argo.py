import yaml

from tpctl.case import CaseInstance


class ArgoCase:
    def __init__(self, case: CaseInstance, image,
                 notify=False, notify_users=None):
        self.case = case
        self.image = image
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
                'generateName': f'tpctl-{case.meta.name}-',
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
                # FIXME: notify can only notify one user temporarily
                'args': [
                    users[0],
                    self.case.meta.name,
                    r'{{workflow.name}}',
                    r'{{inputs.parameters.stage}}',
                    '--status',
                    r'{{inputs.parameters.status}}'
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
