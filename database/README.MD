## TEST DATABASE

it default use mysql database or mariaDB for testing.
default username is root and password is 'a.123456'.

```
python manage.py test
```


### SET ENVIRONMENT

if you want to use custom username and password for database, you can set it in environment variable.

```bash
on linux (mac):
export DB_USERNAME=custom_username
export DB_PASSWORD=custom_password

on windows:
set DB_USERNAME=custom_username
set DB_PASSWORD=custom_password
```
