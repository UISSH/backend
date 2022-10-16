"""
nginx config

server {
    ########BASIC########

    listen 80;
    listen [::]:80;
    root /var/www/flarum.uissh.com/public;
    server_name flarum.uissh.com;
    ########BASIC########


    ########USER########
    index index.php index.html index.htm;
    include /var/www/flarum.uissh.com/.nginx.conf;
    location ~ \.php$ {

        fastcgi_pass  unix:/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include /etc/nginx/fastcgi_params;
    }
    ########USER########

}

"""