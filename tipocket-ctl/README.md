# Tipocket-ctl

Most of the tipocket test cases are supposed to run on K8s and tipocket use [argo](https://github.com/argoproj/argo)
workflow to schedule them. Test case developers need to write several yaml files to
describe the *argo workflow*. However, most of the test case developer are not familiar
with K8s, let alone argo. It is pretty hard for us to write and maintain those yaml files.

Tipocket-ctl is designed to auto-generate argo workflow yaml files and provide
step-by-step guide for developers to **debug** and **run** tipocket test case on K8s.

## Installation

```sh
# Please ensure that you have python3.6+ installed
pip3 install 'git+https://github.com/cosven/tidb-testing.git#egg=tpctl&subdirectory=tipocket-ctl'

# Development install
git clone git@github.com:cosven/tidb-testing.git
cd tidb-testing/tipocket-ctl
pip3 install -e ./

# Help
tpctl --help
```

## Usage

1. customize the tidb cluster config

```sh
echo <<EOF >> config/tpctl-tikv.toml
[raftstore]
delay-sync-us = 0
EOF
```

2. run `tpctl prepare CASE [OPTIONS]` to genrate argo workflow yaml and show steps to run case on K8s

```sh
tpctl prepare scbank2 --build-image --tikv-config config/tpctl-async-raft-tikv.toml --run-time '12h' \
    --nemesis 'random_kill,partition_one,shuffle-leader-scheduler,shuffle-region-scheduler,random-merge-scheduler' \
    --subscriber '@xxx --subscriber '@yyy' \
    --loki-password '' --loki-addr '' --no-purge --feature 'async-raft' \
    --pd-replicas 1 --tidb-replicas 1 --tikv-replicas 7 --image-version "release-4.0-nightly"
```

The command output looks like the following:
```
---pre
Ensure pwd is tipocket directory...
Ensure workspace directory: ./tpctl-build...
---build
Run following commands to rebuild the case
cp config/tpctl-async-raft-tikv.toml tpctl-build/config/
make bank2
cp bin/bank2 tpctl-build/bin/
docker build tpctl-build/ -f tpctl-build/tpctl-dockerfile -t hub.pingcap.net/tpctl/tipocket:bank2-async-raft

docker push hub.pingcap.net/tpctl/tipocket:bank2-async-raft
---deploy
Generating argo workflow tpctl-build/scbank2-async-raft.yaml...
Run following commands to deploy the case
argo submit tpctl-build/scbank2-async-raft.yaml
```
