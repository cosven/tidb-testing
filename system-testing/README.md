# 系统测试

## 关于 hack 脚本

当前的代码风格

1. 函数名以 `st::` 为前缀
2. 命令以 `st-` 为前缀
2. <https://google.github.io/styleguide/shellguide.html>
2. <https://www.davidpashley.com/articles/writing-robust-shell-scripts/>

# 操作手册

## 快速上手

快速部署一个 1pd-1db-3kv 的集群。

1. 设置系统测试的关键环境变量：`export ST_NAMESPACE=st--xxx`。表明你要在哪个 namespace 下进行系统测试，
   集群资源，tekton 任务都会创建在这个 ns 下。

2. 运行 `source SOURCE.sh`，它会给常见命令设置 alias，其中关键的两个是 `k` 和 `tkn`。
   ```
   alias k="kubectl -n $ns"
   alias tkn="tkn -n $ST_NAMESPACE"
   ```

3. 创建 serviceaccount 账号和相关 binding
   ```
   k apply -f rbac/
   kubectl create clusterrolebinding "st-sa-binding-$ST_NAMESPACE" \
     --clusterrole=system-testing --serviceaccount=$ST_NAMESPACE:system-testing
   ```

4. 部署 tasks 和 pipelines
   ```
   k apply -f pipelines/ -f tasks/
   ```

5. 启动 task 和 pipeline。以较简单的 pipeline `st--1pd1db3kv` 为例
   ```
   tkn-start-pipeline st--1pd1db3kv -p run-id=$ST_NAMESPACE
   ```
