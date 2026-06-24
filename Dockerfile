FROM nginxinc/nginx-unprivileged:alpine

RUN chown nginx:nginx /usr/share/nginx/html

USER nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY site/css /usr/share/nginx/html/css
COPY site/images /usr/share/nginx/html/images
COPY site/index.html /etc/nginx/html-templates/index.html.template
COPY docker-entrypoint.d/30-render-index.sh /docker-entrypoint.d/30-render-index.sh
