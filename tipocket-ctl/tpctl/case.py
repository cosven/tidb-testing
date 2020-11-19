class Case:
    def __init__(self, name, binary, maintainers=None):
        self.name = name      # human readable name
        self.binary = binary  # cmd name in tipocket
        self.maintainers = maintainers or []


class CaseInstance:
    def __init__(self, meta: Case, params):
        self.meta = meta
        self.params = params

    def get_cmd(self):
        binpath = f'/bin/{self.meta.binary}'
        for key, value in self.params.items():
            binpath += f' -{key}="{value}"'
        return binpath
