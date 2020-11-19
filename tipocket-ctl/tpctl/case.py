class Case:
    def __init__(self, binary, name, image, params=None):
        self.binary = binary
        self.name = name
        self.image = image
        self._params = params

    @property
    def params(self):
        params = {
            'namespace': f'tpctl-{self.name}',
        }
        params.update(self._params or {})
        return params

    @property
    def cmd(self):
        binpath = f'/bin/{self.binary}'
        for key, value in self.params.items():
            binpath += f' -{key}="{value}"'
        return binpath

    @property
    def namespace(self):
        return self.params['namespace']
