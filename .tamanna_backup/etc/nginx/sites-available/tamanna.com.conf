server {
    listen 80;
    server_name tamanna.com www.tamanna.com;

    root /var/www/tamanna;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}