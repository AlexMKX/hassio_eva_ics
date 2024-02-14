ARG BUILD_FROM
FROM $BUILD_FROM


#RUN apt -y install python3 python3-pip
RUN  apt install -y software-properties-common && \
     add-apt-repository -y ppa:deadsnakes/ppa && apt update && \
     apt -y install python3.11-distutils python3.11 python3.11-venv && \
     curl https://bootstrap.pypa.io/get-pip.py | python3.11 -

RUN mkdir -p /opt/hassio
RUN mkdir -p /mnt/init
# Copy data for add-on
COPY hassio /opt/hassio
RUN pip3.11 install -r /opt/hassio/requirements.txt

RUN chmod a+x /opt/hassio/bin/*
COPY rc.local /mnt/init/rc.local
RUN chmod a+x /mnt/init/rc.local

