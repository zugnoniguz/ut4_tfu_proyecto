FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

RUN apk add --no-cache apache2-utils

COPY 40-htpasswd.sh /docker-entrypoint.d/40-htpasswd.sh
RUN sed -i 's/\r$//' /docker-entrypoint.d/40-htpasswd.sh && chmod +x /docker-entrypoint.d/40-htpasswd.sh

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
