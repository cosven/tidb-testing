import yaml


class Config(str):
    pass


def literal_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(Config, literal_str_representer)


def dump(tidbcluster_dict):
    for component in tidbcluster_dict:
        config = tidbcluster_dict[component]['config']
        if config:
            # strip every line, otherwise pyyaml can't dump with block style
            # https://github.com/yaml/pyyaml/issues/121
            lines = []
            for line in config.split('\n'):
                lines.append(line.strip())
            config = '\n'.join(lines)

            tidbcluster_dict[component]['config'] = Config(config)
    s = yaml.dump(tidbcluster_dict)
    return s
