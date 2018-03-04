FROM nginx:1.9
MAINTAINER Jason Lopez <jasonlopez01@gmail.com>

RUN rm /usr/share/nginx/html/*
RUN rm /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/nginx.conf
COPY configs/nginx.conf /etc/nginx/nginx.conf
COPY configs/default.conf /etc/nginx/conf.d/default.conf

#COPY certs/productionexample.crt /etc/ssl/certs/productionexample.crt
#COPY certs/productionexample.key /etc/ssl/private/productionexample.key
#COPY certs/dhparam.pem /etc/ssl/private/dhparam.pem

CMD ["nginx", "-g", "daemon off;"]
