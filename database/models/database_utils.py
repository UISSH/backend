import subprocess

import pymysql

from base.dataclass import BaseOperatingRes


def execute_sql(sql, root_username="root", root_password="a.123456") -> subprocess.CompletedProcess:
    # cmd = f'mysql -u{root_username} -p{root_password} -e "{sql}"'
    db = pymysql.connect(host='localhost',
                         user=root_username,
                         password=root_password)
    cursor = db.cursor()
    try:
        res = ''
        for item in sql.split(";"):
            item = item.strip()
            if not item:
                ()
                continue
            cursor.execute(item + ";")
            data = cursor.fetchone()
            res += str(data) + "\n"
        ret = subprocess.CompletedProcess(sql, 0, stdout=res)
    except pymysql.err.OperationalError as e:
        ret = subprocess.CompletedProcess(
            sql, e.args[0], stderr=f"{e.args[0]}:{e.args[1]}")
    finally:
        db.close()

    # ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    # if ret.returncode == 0:
    #     pass
    # else:
    #     print(f"{ret.returncode}::{ret.stderr}")

    return ret


def create_new_database(event_id, name, username, password, character="utf8mb4",
                        collation="utf8mb4_general_ci", authorized_ip="localhost", root_username="root",
                        root_password="a.123456"):
    operator_res = BaseOperatingRes.get_instance(event_id)
    operator_res.set_processing()

    create_database_sql = f"CREATE DATABASE IF NOT EXISTS {name} DEFAULT CHARACTER SET " \
                          f"{character} DEFAULT COLLATE {collation};"

    create_user_sql = f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';" \
                      f"flush privileges;"

    authorize_sql = f"GRANT ALL PRIVILEGES ON {name}.* TO '{username}'@'{authorized_ip}' WITH GRANT OPTION;" \
                    f"flush privileges;"

    ret = execute_sql(create_database_sql,
                      root_username=root_username, root_password=root_password)

    if ret.returncode != 0:
        operator_res.msg = f'Failed to create database:{ret.stderr}'
        operator_res.set_failure()
        return

    ret = execute_sql(
        create_user_sql, root_username=root_username, root_password=root_password)
    if ret.returncode != 0:
        operator_res.msg = f'Failed to create user:{ret.stderr}\n,sql::{create_user_sql}'
        operator_res.set_failure()
        return

    ret = execute_sql(authorize_sql, root_username=root_username,
                      root_password=root_password)
    if ret.returncode != 0:
        operator_res.msg = f'Authorization failed:{ret.stderr}'
        operator_res.set_failure()
        return

    operator_res.set_success()


def delete_database(event_id, name, username, authorized_ip="localhost", root_username="root",
                    root_password="a.123456"):
    operator_res = BaseOperatingRes.get_instance(event_id)
    operator_res.set_processing()

    sql = f'DROP database {name};'
    ret = execute_sql(sql, root_username, root_password)
    if ret.returncode != 0:
        operator_res.msg = f'drop database:{ret.stderr}'
        operator_res.set_failure()
        return

    sql = f"DROP user '{username}'@'{authorized_ip}'; "
    ret = execute_sql(sql, root_username, root_password)
    if ret.returncode != 0:
        operator_res.msg = f'drop database:{ret.stderr},sql::{sql}'
        operator_res.set_failure()
        return
    operator_res.set_success()


def update_username_database(event_id, old_username, new_username, authorized_ip='localhost', root_username="root",
                             root_password="a.123456"):
    # https://mariadb.com/kb/en/rename-user/
    operator_res = BaseOperatingRes.get_instance(event_id)
    operator_res.set_processing()

    sql = f"flush privileges;" \
          f"RENAME USER '{old_username}'@'{authorized_ip}' TO '{new_username}'@'{authorized_ip}';" \
          f"flush privileges;"

    ret = execute_sql(sql, root_username=root_username,
                      root_password=root_password)
    if ret.returncode != 0:
        operator_res.msg = f'update user:{ret.stderr},sql::{sql}'
        operator_res.set_failure()
        return
    operator_res.set_success()


def update_password_database(event_id, username, new_password, root_username="root",
                             authorized_ip="localhost",
                             root_password="a.123456"):
    # https://mariadb.com/kb/en/set-password/#example
    operator_res = BaseOperatingRes.get_instance(event_id)
    operator_res.set_processing()

    sql = f"use mysql;" \
          f"SET PASSWORD FOR '{username}'@'{authorized_ip}' = PASSWORD('{new_password}');" \
          f"flush privileges;"

    ret = execute_sql(sql, root_username=root_username,
                      root_password=root_password)
    if ret.returncode != 0:
        operator_res.msg = f'update user:{ret.stderr},sql::{sql}'
        operator_res.set_failure()
        return
    operator_res.set_success()


def import_backup_db(event_id, backup_db_path, root_username="root", root_password="a.123456"):
    operator_res = BaseOperatingRes.get_instance(event_id)
    operator_res.set_processing()
    cmd = f'mysql -u{root_username}  -p{root_password}  <  {backup_db_path}'
    ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, encoding="utf-8")
    if ret.returncode == 0:
        operator_res.set_success()
    else:
        operator_res.set_failure()

    return ret


def export_backup_db(event_id, name, backup_db_path, root_username="root", root_password="a.123456"):
    # mysqldump -uroot-p123456 mydb > /data/mysqlDump/mydb.sql
    operator_res = BaseOperatingRes.get_instance(event_id)
    operator_res.set_processing()
    cmd = f'mysqldump -u{root_username} -p{root_password} {name} > {backup_db_path}'

    ret = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, encoding="utf-8")
    if ret.returncode == 0:
        operator_res.set_success()
    else:
        operator_res.set_failure()

    return ret
