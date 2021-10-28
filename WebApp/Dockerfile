FROM debian:latest

# MAINTAINER Dylan Rae

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi \
    build-essential \
    python \
    python-dev \
    python-pip \ 
    vim \ 
&& apt-get clean \
&& apt-get autoremove \
&& rm -rf /var/lib/apt/lists/*

# python requirements
COPY ./requirements.txt /var/www/apache-flask/app/requirements.txt
RUN pip install -r /var/www/apache-flask/app/requirements.txt

# https requirements (keys and certificates) from root folder to root in container
COPY ./certificate /var/www/apache-flask/app/

# APACHE config from root to inside WebApp
COPY ./apache-flask.conf /etc/apache2/sites-available/apache-flask.conf
RUN a2ensite apache-flask
RUN a2enmod headers

# Copy the .wsgi from inside WebApp to container webapp
# COPY ./WebApp/app.wsgi /var/www/apache-flask/app/WebApp/
# Shouldn't be needed with below line copying everything

# Copy over all of the webapop files not already copied and used
COPY ./WebApp /var/www/apache-flask/app/WebApp/

# Not sure wht this does must necessary for build
RUN a2dissite 000-default.conf
RUN a2ensite apache-flask.conf

# Link apache config to docker logs
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

# Expose ports for http(80) and https(443), (make sure ports are open on router!)
EXPOSE 80
EXPOSE 443

# Set the working directory
WORKDIR /var/www/apache-flask

# Start apache in foreground
CMD /usr/sbin/apache2ctl -D FOREGROUND