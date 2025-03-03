FROM debian:bookworm

RUN apt update \
&& apt install -y qemu-system-x86 gcc python3 openssh-client\
&& apt clean

RUN mkdir /share

COPY ./setup.py /setup.py
RUN chmod +x /setup.py

ENTRYPOINT ["/setup.py"]





