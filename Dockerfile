FROM resin/rpi-raspbian
MAINTAINER Clemens von Schwerin <c.schwerin@hs-ulm.de>
RUN apt-get update \
 && apt-get upgrade --yes \
 && apt-get install iproute2 \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y tshark \
 && yes | dpkg-reconfigure -f noninteractive wireshark-common \
 && addgroup wireshark \
 && usermod -a -G wireshark ${USER:-root} \
 && newgrp wireshark

RUN apt-get install python3 python3-pip python3-dev gcc git iw build-essential net-tools wireless-tools ucf \ 
 && pip3 install howmanypeoplearearound pycrypto pyffx

RUN cd ~ \
 && git clone https://github.com/WiringPi/WiringPi.git \
 && cd WiringPi \
 && git checkout 8d188fa0e00bb8c6ff6eddd07bf92857e9bd533a \
 && ./build
 
RUN cd ~ \
 && git clone https://github.com/clemensvonschwerin/lmic_pi.git \
 && cd lmic_pi/lmic \
 && git checkout generic \
 && make clean \
 && make \
 && cd ../examples/grab-and-send \
 && make clean \
 && make
 
RUN echo "100 0f" > /root/lmic_pi/examples/grab-and-send/measurement.txt

CMD (cd /root/lmic_pi/examples/grab-and-send && nohup ./grab-and-send 2>&1 > grab-and-send.log) & \
 /bin/bash
