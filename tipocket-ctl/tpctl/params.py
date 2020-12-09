import base64

from tpctl.tidb_cluster import ComponentName, ComponentSpec, TidbClusterSpec


def parse_params(params):
    """
    validate params and generate params for test case
    """
    # convert parameters to the format that tipocket test case recognize
    case_params = {}
    for key, value in params.items():
        if key in ['build_image', 'subscriber', 'feature']:
            continue
        # convert True/False to 'true/false'
        if key == 'purge':
            if value is True:
                value = 'true'
            else:
                value = 'false'
        # convert the config path to absolute form
        # read the config file content and encode it to base64
        if key.endswith('_config'):
            # value is a valid config file path
            # read the content in config file and encode it with base64
            # https://github.com/pingcap/tipocket/pull/330
            if value:
                # TODO: catch FileNotExist error or validate the path somewhere
                with open(value) as f:
                    content = f.read()
                content_bytes = bytes(content, 'utf-8')
                b64content = base64.b64encode(content_bytes).decode('utf-8')
                value = f'base64://{b64content}'
        case_params[key.replace('_', '-')] = value
    return case_params


def get_tidb_cluster_spec_from_params(params):
    hub = params['hub']
    repository = params['repository']
    tag = params['image_version']

    components = []
    component_names = ComponentName.list_names()
    for component in component_names:
        config_key = f'{component}_config'
        config_path = params[config_key]
        # NOTE: the program must run in tipocket root directory
        if config_path:
            with open(config_path) as f:
                config = f.read()
        else:
            config = ''
        replicas = params[f'{component}_replicas']
        image = params[f'{component}_image']
        if not image:
            image = f'{hub}/{repository}/{component}:{tag}'
        component = ComponentSpec(component, image, replicas, config)
        components.append(component)
    return TidbClusterSpec.create_from_components(components)
