# Ansible 运维脚本

## 集群部署流程

0. 检查各机器的信息，可以使用 playbook `sysinfo.yaml`
1. 检查是否有残留的 tidb 相关进程（参考本 README）
2. 清理残留的 service `remove_service.yaml`
2. 挂载磁盘，可以使用 playbook `disk.yaml`
3. 检查 numa 信息，可以使用 playbook `numa.yaml`
4. 部署 ntp 服务
5. 调节 CPU 节能策略（参考本 README）
6. 修改机器密码，可以使用 playbook `update_password.yaml`
7. 新建部署目录，在部署目录中按照官方文档部署集群。
   部署目录建议为 `/data-{env}`，env 为 `production` 或者 `testing`。
8. 部署前使用 `tiup cluster check` 命令检查机器及操作系统配置

## 一些便利的命令

### 查看是否有残留的 tidb 相关进程

```sh
ansible -i hosts.ini servers -m shell -a "systemctl status | grep -E 'tikv|tidb|grafana|export|prome'"
```

### 调节 CPU 节能模式

```sh
```
