FROM nginxinc/nginx-unprivileged:alpine
USER nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY site/ /usr/share/nginx/html/
