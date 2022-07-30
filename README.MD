# 介绍

本项目旨在摆脱繁琐的编译安装、命令行配置的运维工作，并尽最大的努力遵循 Linux 通用规范的一个可视化界面。

# 安装

todo

# 规范标准

底层接口尽量调用开源工具提供的接口，目录结构以主流开源工具默认行为为准，不额外造轮子。

节约时间，拥抱美好生活。

## Linux

第一版以最新 Debian (11) 长期支持版本约定俗成的规定为准。

一旦 Linux 长期版本停止维护，本项目也随之停止后续兼容开发以及支持。

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

### MySql

todo

```bash

```

### PHP

todo

```bash

```

### phpmyadmin

todo

```bash

```

### Systemd

**配置文件**

配置文件都应该遵循映射实际配置文件的做法

```bash

# 如实际配置文件存放在
touch /etc/systemd/system/multi-user.target.wants/[name].service

# 应该创建系统软链接
# /etc/systemd/system/multi-user.target.wants/[name].service → /lib/systemd/system/[name].service
ln -s  /etc/systemd/system/multi-user.target.wants/[name].service /lib/systemd/system/[name].service
# 启用
systemctl enable [name].service 
```

## 运行

```bash
gunicorn UISSH.wsgi
```

