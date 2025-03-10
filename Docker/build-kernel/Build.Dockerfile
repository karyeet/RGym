FROM debian:bookworm

# Install the required packages
RUN apt update \
&& apt install --no-install-recommends -y gcc clang make bison flex libelf-dev libssl-dev bc git python3 openssl findutils ca-certificates wget git-lfs \
&& apt clean

# clone kernel source
#RUN git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
#COPY ./linux /linux

RUN mkdir ~/bin && \
    wget https://github.com/seeraven/gitcache/releases/download/v1.0.25/gitcache_v1.0.25_Ubuntu22.04_x86_64 && \
    mv gitcache_v1.0.25_Ubuntu22.04_x86_64 ~/bin/gitcache && \
    chmod +x ~/bin/gitcache && \
    ln -s gitcache ~/bin/git

ENV PATH=/root/bin:$PATH

COPY ./setup.py /setup.py
RUN chmod +x /setup.py

RUN git config --global --add safe.directory '*'

RUN mkdir /share

#CMD ["/setup.py"]
ENTRYPOINT ["/setup.py"]