set -x
echo "hello, tmp.sh"
tidbHost=`echo $cluster_tidb0 | awk -F ":" '{print $1}'`
tidbPort=`echo $cluster_tidb0 | awk -F ":" '{print $2}'`
isDBExist=`mysql -uroot -P "$tidbPort" -h "$tidbHost" -e "use sbtest; show tables;" | grep sbtest > /dev/null && echo "yes" || echo "no"`
if [ "$isDBExist" == "no" ]; then
  mysql -uroot -P4000 -h "$tidbHost" -e "create database sbtest;"
  echo "`date` prepare..."
  sysbench  --mysql-host="$tidbHost" --mysql-port="$tidbPort" --mysql-user=root --tables=16 --table-size=10 --threads=8 --time=60 updates prepare
  echo "`date` prepare...done"
else
  echo "database sysbench already exists"
fi
sysbench  --mysql-host="$tidbHost" --mysql-port="$tidbPort" --mysql-user=root --tables=16 --table-size=10 --threads=8 --time=60 updates run
