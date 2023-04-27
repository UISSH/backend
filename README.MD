# 介绍

本项目旨在摆脱繁琐的编译安装、命令行配置的运维工作，并尽最大的努力遵循 Linux 通用规范的一个可视化面板，提供一键安装、配置、管理、监控、备份、迁移等功能。

并追求面板与系统环境隔离，面板仅仅是一个管理工具，部署的环境以及服务运行也不依赖面板功能。做到面板停止后，您配置的环境与服务依然可以正常运行，使您的系统环境更加稳定、更加安全。

## 环境

 ![debian](https://img.shields.io/badge/OS-Debian%2011%20LTS-brightgreen.svg?style=flat-square&logo=debian)
 ![ubuntu](https://img.shields.io/badge/OS-Ubuntu%2022%20LTS-brightgreen.svg?style=flat-square&logo=ubuntu)
 ![UISSH](https://img.shields.io/badge/Python-3.9--3.11-brightgreen.svg?style=flat-square&logo=python)
 ![UISSH](https://img.shields.io/badge/Django-4.2-brightgreen.svg?style=flat-square&logo=django)
## CI
![django ci](https://github.com/UISSH/backend/actions/workflows/django.yml/badge.svg)
[![Debian 11 CI](https://github.com/UISSH/install-script/actions/workflows/debian_11.yml/badge.svg)](https://github.com/UISSH/install-script/actions/workflows/debian_11.yml)
[![Ubuntu 22.04 CI](https://github.com/UISSH/install-script/actions/workflows/ubuntu_22.04.yml/badge.svg)](https://github.com/UISSH/install-script/actions/workflows/ubuntu_22.04.yml)



## 安装

可使用一键安装脚本快速部署，仅支持 Debian 11 与 Ubuntu 22.04。

- [安装脚本](https://github.com/UISSH/install-script)

## 运行

使用 systemd 管理

```bash
systemctl enable|disable|start|stop| ui-ssh
```

用于开发目的，使用 gunicorn 运行，_某些情况会找不到静态文件（404）_。

```
systemctl stop ui-ssh
gunicorn UISSH.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 
```

## 目录结构

安装后本项目的目录

```bash
# 程序默认位置
/usr/local/uissh
# systemd
/lib/systemd/system/ui-ssh.service
```

其余程序目录以及配置文件（MariaDB、PHP、Nginx）结构都保持默认位置。


## 规范标准

底层接口尽量调用开源工具提供的接口，目录结构以主流开源工具默认行为为准，不额外造轮子。

节约时间，拥抱美好生活。

## Linux

第一版基于 Debian 11 长期支持版本而开发并通过可用性测试，暂时不考虑支持其余发行版。

项目将在 Debian 11 生命周期进入最后两年对 Debian 11 仅仅提供安全更新不额外添加功能，并在 debian 12 长期支持版本上继续开发。

### Nginx

**配置文件**

配置文件都应该遵循映射实际配置文件的做法，

```bash
# 配置文件应该存放在 
touch /etc/nginx/sites-available/[name].conf
# 生效
ln -s /etc/nginx/sites-available/[name].conf /etc/nginx/sites-enabled/[name].conf
```

**API 格式**

原生格式传到前端编辑，然后再保存传回时验证格式有效，无效不保存，提示前端重新编辑。有效则保存并重载或重启对应服务

**SSl 证书**

目录结构遵循 certbot

```bash
# 仅获取证书
certbot certonly \
  -n --nginx --agree-tos \
  -m domain@gmail.com \ 
  -d "domain.com" \
  --server "https://dv.acme-v02.api.pki.goog/directory" # 可选
  
# Certificate is saved at: /etc/letsencrypt/live/domain.com/fullchain.pem
# Key is saved at:         /etc/letsencrypt/live/domain.com/privkey.pem
```

```bash
# 注册第三方机构，如 Google 为例
    certbot register \
    --agree-tos  \
    --email "email@gmail.com" \
    --no-eff-email \
    --server "https://dv.acme-v02.api.pki.goog/directory" \
    --eab-kid "f3acca************7e7d9" \
    --eab-hmac-key "HBUay****************************************WPQ"
```

**网站目录以及权限**

```bash
# 所有网站目录应该创建在 /var/www/[name folder] 下
# 权限应默认为 www-data
chown www-data.www-data -R /var/www/
```

### Systemd

**配置文件**

部署应用都建议使用 systemd 来管理，遵循映射实际配置文件的做法

```bash

# 如实际配置文件存放在
touch /lib/systemd/system/[name].service

# 应该创建系统软链接
ln -s  /lib/systemd/system/[name].service /etc/systemd/system/[name].service
# 启用
systemctl enable [name].service 
```



