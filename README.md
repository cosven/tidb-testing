# Testing TiDB efficiently

## Features

* Tools
  * [artifacts](bin/artifacts) list TiDB/TiKV/Pd latest tarballs
  * [case2pr](bin/case2pr) found the PR that a case is added
* Hack
  * [TiKV dockerfile](hack/tikv-dockerfile) is almost same as the official dockerfile
  * [tidb-operator-yaml](hack/ctx.yaml) is a tidb-cluster CR definition
* Transaction testing
  * [txn-test](txn-test/) provides a demo to reproduce txn-related bug
