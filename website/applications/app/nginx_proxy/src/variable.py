app_parameter = [
    {
        "attr": {},
        "name": "proxy_pass",
        "label": {"default": "title", "en-US": "title"},
        "value": "http://127.0.0.1:32768",
        "required": True,
        "description": {"default": "proxy_pass", "en-US": "proxy_pass"},
    },
]

nginx_config = """
server {
    ########BASIC########
    
    listen 80;
    listen [::]:80;
    root {dir_path};
    server_name {domain};

    ########BASIC########
    
    #**#listen 443 ssl http2;
    #**#listen [::]:443 ssl http2;
    #**#ssl_certificate      /etc/letsencrypt/live/{domain}/fullchain.pem;
    #**#ssl_certificate_key     /etc/letsencrypt/live/{domain}/privkey.pem;
    #**#ssl_trusted_certificate /etc/letsencrypt/live/{domain}/chain.pem;

    #**#ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
    #**#ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    #**#ssl_prefer_server_ciphers on;
    #**#ssl_session_cache shared:SSL:10m;
    #**#ssl_session_timeout 10m;
    #**#error_page 497  https://$host$request_uri;
    
    ########SSL########
    
    ########USER########
    
    # Please add your desired configuration here.
    
    ########USER########

    ########APP########
    location / {
        proxy_pass  http://127.0.0.1:32768;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   Host $host;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
    }
    ########APP########
    
    
}"""
