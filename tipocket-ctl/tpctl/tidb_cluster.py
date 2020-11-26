from enum import Enum


class ComponentName(Enum):
    tidb = 'tidb'
    pd = 'pd'
    tikv = 'tikv'

    @classmethod
    def list_names(cls):
        names = [member.value for _, member in cls.__members__.items()]
        return names


class ComponentSpec:
    def __init__(self, name, image, replicas, config):
        self.name = name
        self.image = image
        self.replicas = replicas
        self.config = config

    def to_json(self):
        return {
            'name': self.name,
            'image': self.image,
            'repliacs': self.replicas,
            'config': self.config
        }


class TidbClusterSpec:
    def __init__(self, pd_spec, tikv_spec, tidb_spec):
        self.pd_spec = pd_spec
        self.tikv_spec = tikv_spec
        self.tidb_spec = tidb_spec

    @classmethod
    def create_from_components(cls, component_specs):
        tidb = pd = tikv = None
        for component_spec in component_specs:
            name = ComponentName(component_spec.name)
            if name == ComponentName.tidb:
                tidb = component_spec
            elif name == ComponentName.pd:
                pd = component_spec
            elif name == ComponentName.tikv:
                tikv = component_spec
        return TidbClusterSpec(tidb_spec=tidb,
                               pd_spec=pd,
                               tikv_spec=tikv)

    def to_json(self):
        return {
            'pd': self.pd_spec.to_json(),
            'tikv': self.tikv_spec.to_json(),
            'tidb': self.tidb_spec.to_json(),
        }
