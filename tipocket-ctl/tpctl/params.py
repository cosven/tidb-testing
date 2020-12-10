from tpctl.tidb_cluster import ComponentName, ComponentSpec, TidbClusterSpec


def parse_params(params):
    """
    validate params and generate params for test case
    """
    # convert parameters to the format that tipocket test case recognize
    case_params = {}
    for key, value in params.items():
        if key in ['build_image', 'subscriber', 'feature', 'cron', 'cron_schedule', 'cron_concurrency_policy', 'cron_starting_deadline_seconds']:
            continue
        # convert True/False to 'true/false'
        if key == 'purge':
            if value is True:
                value = 'true'
            else:
                value = 'false'
        # convert the config path to absolute form
        if key.endswith('_config'):
            if value:
                value = '/' + value
        case_params[key.replace('_', '-')] = value
    return case_params


def get_tidb_cluster_spec_from_params(params):
    hub = params['hub']
    repository = params['repository']
    tag = params['image_version']

    components = []
    component_names = ComponentName.list_names()
    for component in component_names:
        config_path = params[f'{component}_config']
        # FIXME: the program must run in tipocket root directory
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
