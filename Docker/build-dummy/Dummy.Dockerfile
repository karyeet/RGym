FROM debian:bookworm

# Install the required packages
RUN apt update \
&& apt install --no-install-recommends -y gcc make bison flex libelf-dev libssl-dev bc git python3 openssl findutils \
&& apt clean

# clone kernel source
#RUN git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
COPY ./linux /linux

COPY ./dummy.py /dummy.py
RUN chmod +x /dummy.py

COPY ./make.log /make.log

RUN git config --global --add safe.directory '*'

RUN mkdir /share

#CMD ["/setup.py"]
ENTRYPOINT ["/dummy.py"]