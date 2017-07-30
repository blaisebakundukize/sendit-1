FROM python:3.5.1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    gfortran \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    libhdf5-dev \
    libgeos-dev \
    build-essential \
    openssl \
    nginx \
    wget \
    vim

RUN pip install --upgrade pip
RUN pip install cython
RUN pip install numpy
RUN pip install scikit-learn pandas h5py matplotlib
RUN pip install uwsgi
RUN pip install Django==1.11.2
RUN pip install social-auth-app-django
RUN pip install social-auth-core[saml]
RUN pip install djangorestframework
RUN pip install django-rest-swagger
RUN pip install django-filter
RUN pip install django-taggit
RUN pip install django-form-utils
RUN pip install django-crispy-forms
RUN pip install django-taggit-templatetags
RUN pip install django-dirtyfields
RUN pip install 'dropbox==1.6'
RUN pip install 'django-dbbackup<2.3'
RUN pip install psycopg2
RUN pip install numexpr
RUN pip install shapely
RUN pip install Pillow
RUN pip install requests
RUN pip install requests-oauthlib
RUN pip install python-openid
RUN pip install django-sendfile
RUN pip install django-polymorphic
RUN pip install celery[redis]==3.1.25
RUN pip install django-celery
RUN pip install scikit-learn
RUN pip install django-cleanup
RUN pip install django-chosen
RUN pip install opbeat
RUN pip install 'django-hstore==1.3.5'
RUN pip install django-datatables-view
RUN pip install django-oauth-toolkit
RUN pip install simplejson
RUN pip install django-gravatar2
RUN pip install pygments
RUN pip install django-lockdown
RUN pip install xmltodict
RUN pip install grpcio
RUN pip install som
RUN pip install django-cors-headers
RUN pip install django-user-agents
RUN pip install django-guardian
RUN pip install pyinotify


# Install pydicom
WORKDIR /tmp
RUN git clone https://github.com/vsoch/pydicom
WORKDIR pydicom
RUN python setup.py install

RUN mkdir /code
RUN mkdir -p /var/www/images
RUN mkdir /data
WORKDIR /code
ADD . /code/
RUN /usr/bin/yes | pip uninstall cython
RUN apt-get remove -y gfortran

# This is needed for certificate on server, interactive run for now
WORKDIR /tmp
RUN openssl genrsa -out server.key 4096 && mv server.key /etc/ssl/certs
#RUN openssl dhparam -out dhparam.pem 4096 && mv dhparam.pem /etc/ssl/certs

RUN cp /code/csr_details.txt /tmp
WORKDIR /tmp
RUN echo CN = \"`hostname`\" >> csr_details.txt

# call openssl now by piping the newly created file in
RUN openssl req -new -sha256 -nodes -out server.csr -newkey rsa:2048 -keyout server.key -subj="/C=US/ST=California/L=San Mateo County/O=End Point/OU=Sendit"
#config <`cat csr_details.txt`
RUN openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

RUN cp server.key /etc/ssl/private
RUN cp server.crt /etc/ssl/certs

# Create the challenge folder in the webroot
RUN mkdir -p /var/www/html/.well-known/acme-challenge/
RUN chown $USER -R /var/www/html/

# Get a signed certificate with acme-tiny
RUN mkdir /opt/acme_tiny
RUN git clone https://github.com/diafygi/acme-tiny
RUN mv acme-tiny /opt/acme-tiny/
RUN chown $USER -R /opt/acme-tiny

RUN python /opt/acme-tiny/acme_tiny.py --account-key /etc/ssl/certs/server.key --csr /etc/ssl/certs/server.csr --acme-dir /var/www/html/.well-known/acme-challenge/ > ./signed.crt

RUN wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
RUN cat signed.crt intermediate.pem > chained.pem
RUN mv chained.pem /etc/ssl/certs/

# Reinstall root certificates
RUN apt-get install -y ca-certificates
RUN mkdir /usr/local/share/ca-certificates/cacert.org
RUN wget -P /usr/local/share/ca-certificates/cacert.org http://www.cacert.org/certs/root.crt http://www.cacert.org/certs/class3.crt
RUN update-ca-certificates

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD /code/run_uwsgi.sh

EXPOSE 3031
