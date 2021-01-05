# Tipocket-ctl

Most of the tipocket test cases are supposed to run on K8s and tipocket use [argo](https://github.com/argoproj/argo)
workflow to schedule them. Test case developers need to write several yaml files to
describe the *argo workflow*. However, most of the test case developer are not familiar
with K8s, let alone argo. It is pretty hard for us to write and maintain those yaml files.

Tipocket-ctl is designed to auto-generate argo workflow yaml files and provide step-by-step
guide for developers to **debug** and **run** tipocket test case on K8s.

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

```sh
tpctl deploy --run-time='5m' --subscriber '@slack_id' -- bin/resolve-lock -enable-green-gc=false
```

The command output looks like the following:
```
Case name is resolve-lock
Generating command for running case...
/bin/resolve-lock -enable-green-gc=false -run-time="5m" -round="1" -client="5" -nemesis="" -purge="false" -delNS="false" -namespace="tpctl-resolve-lock-universal" -hub="docker.io" -repository="pingcap" -image-version="nightly" -tikv-image="" -tidb-image="" -pd-image="" -tikv-config="" -tidb-config="" -pd-config="" -tikv-replicas="5" -tidb-replicas="1" -pd-replicas="1" -storage-class="local-storage" -loki-addr="" -loki-username="" -loki-password=""
Generating argo workflow tpctl-resolve-lock-universal.yaml...
Run following commands to deploy the case
argo submit tpctl-resolve-lock-universal.yaml
```
