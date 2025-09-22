ARG CC_BASE_IMAGE
ARG CC_IMAGE_VERSION
ARG GITCACHE_VERSION="1.0.25"

# git cache wheelhouse
FROM python:3.10-slim AS wheelbuilder
ARG GITCACHE_VERSION
RUN python -m pip install -U pip \
 && echo "gitcache @ https://github.com/seeraven/gitcache/releases/download/v${GITCACHE_VERSION}/gitcache-${GITCACHE_VERSION}-py3-none-any.whl" > /tmp/reqs.txt \
 && pip download -d /wheelhouse -r /tmp/reqs.txt

FROM $CC_BASE_IMAGE:$CC_IMAGE_VERSION
ARG GITCACHE_VERSION

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    release="$([ -r /etc/os-release ] && . /etc/os-release; printf %s "${VERSION_CODENAME:-}")"; \
    if [ -z "$release" ] && [ -r /etc/debian_version ]; then \
        v="$(sed 's/\..*//' /etc/debian_version)"; \
    case "$v" in \
        8)  release=jessie ;; \
        9)  release=stretch ;; \
        10) release=buster ;; \
        11) release=bullseye ;; \
        12) release=bookworm ;; \
    esac; \
    fi; \
    if [ "$release" = jessie ] || [ "$release" = stretch ] || [ "$release" = buster ]; then \
        echo ">>> EOL Debian $release, switching to archive"; \
        : > /etc/apt/sources.list; \
        printf 'deb http://archive.debian.org/debian %s main contrib non-free\n' "$release" >> /etc/apt/sources.list; \
        printf 'deb http://archive.debian.org/debian-security %s/updates main contrib non-free\n' "$release" >> /etc/apt/sources.list; \
        # Relax apt checks (expired signatures, weak repos, unauth repos)
        echo 'Acquire::Check-Valid-Until "false";'             >  /etc/apt/apt.conf.d/99-archive-eol; \
        echo 'Acquire::AllowInsecureRepositories "true";'     >> /etc/apt/apt.conf.d/99-archive-eol; \
        echo 'Acquire::AllowWeakRepositories "true";'         >> /etc/apt/apt.conf.d/99-archive-eol; \
        echo 'APT::Get::AllowUnauthenticated "true";'         >> /etc/apt/apt.conf.d/99-archive-eol; \
        # Rewrite any extra list files if present
        if ls /etc/apt/sources.list.d/*.list >/dev/null 2>&1; then \
            sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list.d/*.list || true; \
            sed -i 's|http://security.debian.org|http://archive.debian.org/debian-security|g' /etc/apt/sources.list.d/*.list || true; \
        fi; \
        apt-get -o Acquire::Check-Valid-Until=false \
            -o Acquire::AllowInsecureRepositories=true \
            -o Acquire::AllowWeakRepositories=true \
            -o APT::Get::AllowUnauthenticated=true update; \
        # gpg packages differ by release
        case "$release" in \
            jessie|stretch) gpg_pkgs="gnupg-agent dirmngr" ;; \
            buster)         gpg_pkgs="gnupg dirmngr" ;; \
        esac; \
    else \
        echo ">>> Debian ${release:-unknown}, using default mirrors"; \
        gpg_pkgs="gpg-agent"; \
    fi \
    # install required packages
    && apt-get update \
    && apt-get install --no-install-recommends -y software-properties-common $gpg_pkgs make bsdmainutils bison flex libelf-dev libssl-dev bc git openssl findutils ca-certificates wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libreadline-dev libffi-dev \
    && apt-get clean \ 
    && rm -rf /var/lib/apt/lists/*

# install python
RUN wget https://www.python.org/ftp/python/3.10.18/Python-3.10.18.tgz && \
    tar xzf Python-3.10.18.tgz && \
    cd Python-3.10.18 && \
    ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make altinstall && \
    /usr/local/bin/python3.10 -m ensurepip --default-pip

# install gitcache
COPY --from=wheelbuilder /wheelhouse /wheelhouse
RUN mkdir ~/bin && \
    /usr/local/bin/pip3.10 install --no-index --find-links=/wheelhouse gitcache==${GITCACHE_VERSION} && \
    ln -s $(which gitcache) ~/bin/git

ENV PATH=/root/bin:$PATH

COPY ./setup.py /setup.py
RUN chmod +x /setup.py

RUN git config --global --add safe.directory '*'

RUN mkdir /share

#CMD ["/setup.py"]
ENTRYPOINT ["/usr/local/bin/python3.10", "/setup.py"]