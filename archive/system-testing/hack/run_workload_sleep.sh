#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Usage: $0 <run-id>"
    exit 1
fi

run_id=$1
kubectl -n $ST_NAMESPACE get tct $run_id > /dev/null \
    || (echo "tct $run_id not found." && exit 1)
kubectl -n $ST_NAMESPACE get tr workload > /dev/null \
    || (echo "Node workload not found." && exit 1)

cat <<EOF | kubectl -n $ST_NAMESPACE apply -f -
apiVersion: naglfar.pingcap.com/v1
kind: TestWorkload
metadata:
  name: "$run_id-sleep"
spec:
  clusterTopologies:
    - name: "$run_id"
      aliasName: cluster
  workloads:
    - name: "$run_id"
      dockerContainer:
        resourceRequest:
          name: "$run_id"
          node: workload
        image: hub.pingcap.net/mahjonp/bench-toolset
        imagePullPolicy: IfNotPresent
        command:
          - /bin/bash
          - -c
          - |
            env
            sleep 600
EOF
