module github.com/cosven/tidb-testing/easy

go 1.14

require (
	github.com/pingcap/log v0.0.0-20200828042413-fce0951f1463
	go.etcd.io/etcd/v3 v3.0.0-00010101000000-000000000000
	go.uber.org/zap v1.15.0
)

replace go.etcd.io/etcd/v3 => github.com/etcd-io/etcd/v3 v3.3.0-rc.0.0.20200826232710-c20cc05fc548
