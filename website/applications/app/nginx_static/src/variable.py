app_parameter = [
    {
        "attr": {},
        "name": "name",
        "label": {"default": "title", "en-US": "title"},
        "value": "New website!",
        "required": True,
        "description": {"default": "your website title", "en-US": "your website title"},
    },
    {
        "attr": {},
        "name": "text",
        "label": {"default": "text", "en-US": "text"},
        "required": True,
        "value": "与君初相识，犹如故人归。嗨，别来无恙！ <br> Hello World！",
        "description": {
            "default": "what about do u you say?",
            "en-US": "what about do u you say?",
        },
    },
    {
        "attr": {},
        "name": "email",
        "label": {"default": "email", "en-US": "email"},
        "value": None,
        "required": False,
        "description": {
            "default": "your contact information",
            "en-US": "your contact information",
        },
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
    
    index index.html;
    location / {
        try_files $uri $uri/ =404;
    }
    
    ########APP########
    
    
}"""
