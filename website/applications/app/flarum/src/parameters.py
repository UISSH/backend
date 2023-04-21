app_parameter = [
    {
        "attr": {},
        "name": "username",
        "label": {"default": "username", "en-US": "username"},
        "value": "root",
        "required": True,
        "description": {"default": "super user name", "en-US": "super user name"},
    },
    {
        "attr": {},
        "name": "password",
        "label": {"default": "password", "en-US": "password"},
        "value": "password",
        "required": True,
        "description": {
            "default": "super user password",
            "en-US": "super user password",
        },
    },
    {
        "attr": {},
        "name": "email",
        "label": {"default": "email", "en-US": "email"},
        "value": "admin@mail.com",
        "required": True,
        "description": {"default": "super user email", "en-US": "super user email"},
    },
]


flarum_nginx_config = """

    index index.php index.html index.htm;
    include {root_dir}/.nginx.conf;
    
    location ~ \.php$ {
        fastcgi_pass  unix:/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include /etc/nginx/fastcgi_params;
    }
    """
