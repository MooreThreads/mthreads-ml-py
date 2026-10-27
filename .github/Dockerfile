FROM ubuntu:22.04

LABEL name="Moore Threads Mtml Python Library CI Base Image"
LABEL summary="Python Library CI Base Image for Moore Threads Mtml"
LABEL description="See summary"
LABEL vendor="MOORE THREADS CORPORATION"
LABEL maintainer="MOORE THREADS CORPORATION <mt-sw-cloudcomputing@mthreads.com>"


ENV DEBIAN_FRONTEND=noninteractive

RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak \
    && sed -i 's@//.*archive.ubuntu.com@//mirrors.aliyun.com@g' /etc/apt/sources.list \
    && sed -i 's@//.*security.ubuntu.com@//mirrors.aliyun.com@g' /etc/apt/sources.list

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-dev build-essential ca-certificates \
        git curl \
        libicu-dev \
        sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN groupdel render 2>/dev/null || true \
    && sed -i '/:109:/d' /etc/group

RUN groupadd -g 109 render

RUN groupadd -g 1001 mccxadmin

RUN useradd -l -u 1000 -g 1001 -G video,render -s /bin/bash -m mccxadmin

RUN echo "mccxadmin ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/mccxadmin \
    && chmod 0440 /etc/sudoers.d/mccxadmin

WORKDIR /app

RUN chown -R mccxadmin:mccxadmin /app

USER mccxadmin

CMD ["/bin/bash"]
