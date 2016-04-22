FROM docketbook/rethinkdb-alpine:2.3.0
MAINTAINER Tom Midson <tm@docketbook.io>

USER root

RUN set -x \
        && apk add --no-cache --virtual .build-deps \
        python \
        python-dev \
        py-pip \
        build-base \
        && pip install rethinkdb python-Consul requests

# Add ContainerPilot and set its configuration file path
ENV CONTAINERPILOT_VER 2.0.1
ENV CONTAINERPILOT file:///etc/containerpilot.json

RUN export CONTAINERPILOT_CHECKSUM=a4dd6bc001c82210b5c33ec2aa82d7ce83245154 \
    && curl -Lso /tmp/containerpilot.tar.gz \
        "https://github.com/joyent/containerpilot/releases/download/${CONTAINERPILOT_VER}/containerpilot-${CONTAINERPILOT_VER}.tar.gz" \
    && echo "${CONTAINERPILOT_CHECKSUM}  /tmp/containerpilot.tar.gz" | sha1sum -c \
    && tar zxf /tmp/containerpilot.tar.gz -C /usr/local/bin \
    && rm /tmp/containerpilot.tar.gz

# configure ContainerPilot and MySQL
COPY etc/* /etc/
COPY bin/* /usr/local/bin/

# override the parent entrypoint
ENTRYPOINT []

EXPOSE 29015 28015 8080

# use --console to get error logs to stderr
CMD [ "containerpilot", \
      "rethinkdb", \
      "--config-file", \
      "/etc/rethink.conf", \
      "--bind", \
      "all" \
]
