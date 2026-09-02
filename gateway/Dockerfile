FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

# nginx runs in foreground
CMD ["nginx", "-g", "daemon off;"]
