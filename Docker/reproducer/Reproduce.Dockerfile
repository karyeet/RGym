FROM gcr.io/syzkaller/env:latest AS syz-builder

RUN cd /syzkaller/gopath/src/github.com/google \
&& rm -r syzkaller \
&& git clone https://github.com/google/syzkaller.git \
&& cd ./syzkaller \
&& make \
&& mkdir /syzprogs && \
cp ./bin/linux_amd64/* /syzprogs

FROM debian:bookworm

RUN apt update \
&& apt install -y qemu-system-x86 gcc python3 git openssh-client\
&& apt clean

COPY --from=syz-builder /syzprogs /syzprogs

RUN mkdir /share

COPY ./setup.py /setup.py
RUN chmod +x /setup.py

ENTRYPOINT ["/setup.py"]





