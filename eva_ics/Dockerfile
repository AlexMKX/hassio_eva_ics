ARG BUILD_FROM
FROM $BUILD_FROM


RUN apt -y install python3 python3-pip
RUN mkdir -p /opt/hassio
RUN mkdir -p /mnt/init
# Copy data for add-on
COPY hassio /opt/hassio
RUN pip3 install -r /opt/hassio/requirements.txt

RUN chmod a+x /opt/hassio/gen_modbus.py
COPY rc.local /mnt/init/rc.local
RUN chmod a+x /mnt/init/rc.local

