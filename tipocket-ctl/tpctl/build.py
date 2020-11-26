from tpctl.dockerfile import local_dockerfile


class Build:
    """
    output: artifacts
    """
    def __init__(self, env, feature, binary, build_image, config_filepaths):
        self._env = env
        self._feature = feature
        self._binary = binary
        self._config_filepaths = config_filepaths
        self._build_image = build_image
        self._image = None

    def prepare(self):
        if self._build_image:
            dockerfile = f'{self._env.dir_root}/tpctl-dockerfile'
            with open(dockerfile, 'w') as f:
                f.write(local_dockerfile)
            image = f'hub.pingcap.net/tpctl/tipocket:{self._binary}-{self._feature}'
        else:
            image = 'pingcap/tipocket:latest'
        self._image = image

    def get_howto_cmds(self):
        binary = self._binary
        image = self.get_image()

        root_dir = self._env.dir_root
        config_dir = self._env.dir_config
        bin_dir = self._env.dir_bin
        cmds = []
        if self._build_image:
            for config_filepath in self._config_filepaths:
                if config_filepath:
                    cmds.append(f'cp {config_filepath} {config_dir}/')
            cmds.append(f'make {binary}')
            cmds.append(f'cp bin/{binary} {bin_dir}/')
            cmds.append(f'docker build {root_dir}/'
                        f' -f {root_dir}/tpctl-dockerfile'
                        f' -t {image}')
            cmds.append(f'')
            cmds.append(f'docker push {image}')
        return cmds

    def get_image(self):
        """
        artifacts
        """
        return self._image
