FROM debian:buster

# MAINTAINER Dylan Rae

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    python3.7 \
    python3.7-dev \
    python3-pip \ 
    vim \ 
&& apt-get clean \
&& apt-get autoremove \
&& rm -rf /var/lib/apt/lists/*

# Python package management and basic dependencies
# RUN apt-get install -y python3.7 python3.7-dev python3.7-pip

# Register the version in alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Set python 3 as the default python
RUN update-alternatives --set python /usr/bin/python3.7

# Upgrade pip to latest version
# RUN python -m ensurepip --upgrade

RUN python3 --version
RUN pip3 list

# python requirements
COPY ./requirements.txt /var/www/apache-flask/app/requirements.txt
RUN pip3 install -r /var/www/apache-flask/app/requirements.txt

# https requirements (keys and certificates) from root folder to root in container
# COPY ./certificate /var/www/apache-flask/app/

# APACHE config from root to inside WebApp
COPY ./apache-flask.conf /etc/apache2/sites-available/apache-flask.conf
# RUN a2ensite apache-flask
RUN a2ensite apache-flask.conf
RUN a2enmod headers
RUN a2enmod ssl

# Not sure wht this does must necessary for build
# RUN a2dissite 000-default.conf

# Copy the .wsgi from inside WebApp to container webapp
# COPY ./WebApp/app.wsgi /var/www/apache-flask/app/WebApp/
# Shouldn't be needed with below line copying everything

# Copy over all of the webapop files not already copied and used
COPY ./WebApp /var/www/apache-flask/app/WebApp/app.wsgi
COPY ./WebApp /var/www/apache-flask/app/WebApp/
COPY ./certificate /etc/apache2/certificate

# Link apache config to docker logs
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

# Expose ports for http(80), https(443), sql(3306), and mqtt(1883). (make sure ports are open on router!)
EXPOSE 80 
EXPOSE 443 
EXPOSE 3306 
EXPOSE 1883

# Set the working directory
WORKDIR /var/www/apache-flask

# Start apache in foreground
CMD /usr/sbin/apache2ctl -D FOREGROUND
# CMD /usr/sbin/apache2ctl configtest