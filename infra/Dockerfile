# nginx/Dockerfile
FROM nginx:alpine

COPY nginx.conf /etc/nginx/templates/default.conf.template

# Экспортируем порты
EXPOSE 80 443

# Запускаем nginx в foreground
CMD ["nginx", "-g", "daemon off;"]