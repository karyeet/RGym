ARG CC_BASE_IMAGE
ARG CC_IMAGE_VERSION

FROM $CC_BASE_IMAGE:$CC_IMAGE_VERSION
# Install the required packages
RUN apt update \
&& apt install --no-install-recommends -y software-properties-common gpg-agent make bison flex libelf-dev libssl-dev bc git openssl findutils ca-certificates wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libreadline-dev libffi-dev \
&& apt clean

# clone kernel source
#RUN git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
#COPY ./linux /linux

# install python
RUN wget https://www.python.org/ftp/python/3.10.18/Python-3.10.18.tgz && \
    tar xzf Python-3.10.18.tgz && \
    cd Python-3.10.18 && \
    ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make altinstall

# ensure pip
RUN /usr/local/bin/python3.10 -m ensurepip --upgrade && \
    /usr/local/bin/pip3.10 install --no-cache-dir --upgrade pip setuptools wheel

# install gitcache
RUN mkdir ~/bin && \
    wget https://github.com/seeraven/gitcache/releases/download/v1.0.25/gitcache-1.0.25-py3-none-any.whl && \
    pip3 install gitcache-1.0.25-py3-none-any.whl && \
    ln -s $(which gitcache) ~/bin/git

ENV PATH=/root/bin:$PATH

COPY ./setup.py /setup.py
RUN chmod +x /setup.py

RUN git config --global --add safe.directory '*'

RUN mkdir /share

#CMD ["/setup.py"]
ENTRYPOINT ["/setup.py"]