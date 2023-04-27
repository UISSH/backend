## 测试数据

使用mysql数据库或mariaDB进行测试，默认用户名是root，密码是'2d46274325564ced'。

```
python manage.py test
```


### 设置环境变量

如果你想使用自定义的用户名和密码，可以在环境变量中设置。

```bash
on linux (mac):
export DB_USERNAME=custom_username
export DB_PASSWORD=custom_password

on windows:
set DB_USERNAME=custom_username
set DB_PASSWORD=custom_password
```

### LoadMap 

默认预装 mariaDB 数据库，对外只需要对数据库的创建、删除、修改、查询、备份、恢复、导出、导入等操作进行抽象，对外提供统一的接口，方便后续的扩展。

在抽象设计完成后，需要支持 MariaDB、MongoDB 等数据库的操作。


