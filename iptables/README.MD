# 本模块的设计概览

主要利用 UFW 提供对系统防火墙规则基本的增删改查，这样可以无视网络包过滤工具的差异。


## 功能实现

需要实现的功能

### 安装 UFW 工具

需要判断系统是否已经安装了 UFW 工具，如果没有安装则需要安装。

### 配置 UFW 工具

需要配置 UFW 工具的默认策略，以及默认的日志级别。开放默认的端口 22,80,443,8080。

### 列出防火墙规则

```python
import subprocess

# 获取规则列表
def get_rules():
    result = subprocess.run(['ufw', 'status', 'numbered'], capture_output=True, text=True)
    output = result.stdout
    lines = output.strip().split('\n')[4:]  # 跳过前4行输出，获取规则行列表
    rules = []
    for line in lines:
        # 解析规则行
        parts = line.strip().split()
        number = parts[0]
        status = parts[1]
        port = parts[2]
        rules.append({'id': number, 'status': status, 'port': port})
    return rules
```



### 删除防火墙规则

### 添加防火墙规则

### 清空防火墙规则

### 重启防火墙

## 测试

