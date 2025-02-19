from debian:bullseye

# Install the required packages
RUN apt update && apt install -y gcc make bison flex libelf-dev libssl-dev bc git

# clone kernel source
#RUN git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
COPY ./linux /linux

COPY ./setup.sh /setup.sh
RUN chmod +x /setup.sh

RUN mkdir /share

CMD ["/setup.sh"]

