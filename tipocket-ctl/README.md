# Tipocket-ctl

Most of the tipocket test cases are supposed to run on K8s and tipocket use [argo](https://github.com/argoproj/argo)
workflow to schedule them. Test case developers need to write several yaml files to
describe the *argo workflow*. However, most of the test case developer are not familiar
with K8s, let alone argo. It is pretty hard for us to write and maintain those yaml files.

Tipocket-ctl is designed to auto-generate argo workflow yaml files and provide
step-by-step guide for developers to **debug** and **run** tipocket test case on K8s.

## Install

```sh
# Please ensure that you have python3.6+ installed
pip3 install 'git+https://github.com/cosven/tidb-testing.git#egg=tpctl&subdirectory=tipocket-ctl'

# Check if install succeed
tpctl --help
```

## Usage

1. customize the tidb cluster config

```sh
echo <<EOF >> config/tpctl-tikv.toml
[pessimistic-txn]
pipelined = true
EOF
```

2. run `tpctl prepare CASE [OPTIONS]` to genrate argo workflow yaml and show steps to run case on K8s

```sh
tpctl prepare pipelined-locking --tikv-config config/tpctl-tikv.toml \
    --hub hub.pingcap.net --repository qa --image-version 'master-failpoint' --build-image \
    --client 1 --run-time 10h
```

> ```
> Ensure pwd is tipocket directory...
> Ensure build directory: ./tpctl-build...
> Generating argo workflow tpctl-build/pipelined-locking.yaml...
>
> --------------------
> You can run pipelined-locking with following commands:
>
> cp config/tpctl-tikv.toml tpctl-build/config/
> make pipelined-locking
> cp bin/pipelined-locking tpctl-build/bin/
> docker build tpctl-build/ -f tpctl-build/tpctl-dockerfile -t hub.pingcap.net/tpctl/tipocket:pipelined-locking
>
> docker push hub.pingcap.net/tpctl/tipocket:pipelined-locking
> argo submit tpctl-build/pipelined-locking.yaml
> ```
