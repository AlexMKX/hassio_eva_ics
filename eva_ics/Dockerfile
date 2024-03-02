ARG BUILD_FROM=altertech/eva-ics4:latest
FROM $BUILD_FROM


#RUN curl https://x.bma.ai/d/ftDqaLFOKA8d8Ylt/ZcY88QDXKAgZunFG/eva-controller-modbus -o /opt/eva4/svc/eva-controller-modbus
#RUN chmod a+x /opt/eva4/svc/eva-controller-modbus


#RUN apt -y install python3 python3-pip
RUN  apt install -y software-properties-common python3-pip && \
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
RUN /opt/eva4/sbin/venvmgr add eva4-controller-py
RUN /opt/eva4/sbin/venvmgr add jinja2
COPY overlay /
RUN mkdir -p /opt/eva4/runtime/xc/py
