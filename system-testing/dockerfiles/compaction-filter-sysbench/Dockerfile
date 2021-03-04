# https://github.com/PingCAP-QE/bench-toolset/blob/master/Dockerfile
FROM hub.pingcap.net/mahjonp/bench-toolset
RUN mkdir -p /data/apps/compaction-filter-sysbench/
WORKDIR /data/apps/compaction-filter-sysbench/

ADD common.lua ./
ADD updates.lua ./

# Output: hub.pingcap.net/system-testing/compaction-filter-sysbench:210304
