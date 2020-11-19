import yaml

from tpctl.case import Case


class ArgoCase:
    def __init__(self, case: Case):
        self.case = case

    def gen_workflow(self):
        case = self.case
        workflow = {
            'metadata': {
                'generateName': f'tpctl-{case.name}-',
                'namespace': 'argo',
            },
            'spec': {
                'entrypoint': 'main',
                'templates': [
                    {
                        'name': 'main',
                        'steps': [
                            [self.gen_case_step(),]
                        ]
                    },
                    self.gen_case_template(),
                ],
            },
        }
        return workflow

    def gen_case_step(self):
        case = self.case
        step = {
            'name': f'call-{case.name}',
            'template': self._get_case_template_name(),
        }
        return step

    def gen_case_template(self):
        case = self.case
        return {
            'name': self._get_case_template_name(),
            'outputs': {
                'artifacts': [
                    {
                        'name': 'case-log',
                        'archiveLogs': True,
                        'path': '/var/run/tipocket-logs',
                    },
                ]
            },
            'metadata': {
                'labels': {
                    'ns': case.namespace,
                }
            },
            'container': {
                'name': case.name,
                'image': case.image,
                'imagePullpolicy': 'Always',
                'command': ['sh', '-c', case.cmd]
            }
        }

    def _get_case_template_name(self):
        return self.case.name
