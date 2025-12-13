server {
    listen 80;
    server_name tamanna.io www.tamanna.io;

    root /var/www/tamanna;
    index index.html index.php;

    location / {
        try_files $uri $uri/ =404;
    }
}