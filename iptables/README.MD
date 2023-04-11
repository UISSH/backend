# 本模块的设计概览

主要利用 UFW 提供对系统防火墙规则基本的增删改查，这样可以无视网络包过滤工具的差异。


## 安装 UFW 工具

需要判断系统是否已经安装了 UFW 工具，如果没有安装则需要安装。

## 配置 UFW 工具

需要配置 UFW 工具的默认策略，以及默认的日志级别。开放默认的端口 22,80,443,8080。

## 列出防火墙规则

基于 `ufw status numbered`，可以列出当前系统的防火墙规则。
```
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    Anywhere                  
[ 2] 80/tcp                     ALLOW IN    Anywhere                  
[ 3] 443/tcp                    ALLOW IN    Anywhere                  
[ 4] 8080/tcp                   ALLOW IN    Anywhere                  
[ 5] 22/tcp (v6)                ALLOW IN    Anywhere (v6)             
[ 6] 80/tcp (v6)                ALLOW IN    Anywhere (v6)             
[ 7] 443/tcp (v6)               ALLOW IN    Anywhere (v6)             
[ 8] 8080/tcp (v6)              ALLOW IN    Anywhere (v6)
```
## 删除防火墙规则
```bash
# 比如要删除第 8 条规则
echo "y" | ufw delete 8
```
## 添加防火墙规则

### 端口

```bash
# 允许/拒绝 8080 端口
ufw allow/deny 8080
```

### 端口范围

```bash
# 允许/拒绝 8080-8090 端口范围
ufw allow/deny 8080:8090
```

### 协议

```bash
#  允许/拒绝 8080 端口的 TCP 协议
ufw allow/deny 8080/tcp
```

### IP 地址

```bash
#  允许/拒绝 8.8.8.8
ufw allow/deny from 8.8.8.8
```


### 清空防火墙规则

```
# 清空防火墙规则
ufw --force reset
```

### 重启防火墙



