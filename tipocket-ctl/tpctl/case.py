class Case:
    def __init__(self, name, maintainers=None):
        self.name = name      # human readable name
        self.maintainers = maintainers or []


class CaseInstance:
    def __init__(self, meta: Case, binary, params):
        self.meta = meta
        self.binary = binary
        self.params = params

    def get_cmd(self):
        binpath = f'/bin/{self.binary}'
        for key, value in self.params.items():
            binpath += f' -{key}="{value}"'
        return binpath
