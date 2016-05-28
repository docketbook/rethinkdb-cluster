FROM rethinkdb:2.3.2
MAINTAINER Tom Midson <tm@docketbook.io>

USER root

RUN set -x \ 
    && apt-get update \
    && apt-get install -y curl

# Add ContainerPilot and set its configuration file path
ENV CONTAINERPILOT_VER 2.1.2
ENV CONTAINERPILOT file:///etc/containerpilot.json

RUN export CONTAINERPILOT_CHECKSUM=c31333047d58ba09d647d717ae1fc691133db6eb \
    && curl -Lso /tmp/containerpilot.tar.gz \
        "https://github.com/joyent/containerpilot/releases/download/${CONTAINERPILOT_VER}/containerpilot-${CONTAINERPILOT_VER}.tar.gz" \
    && echo "${CONTAINERPILOT_CHECKSUM}  /tmp/containerpilot.tar.gz" | sha1sum -c \
    && tar zxf /tmp/containerpilot.tar.gz -C /usr/local/bin \
    && rm /tmp/containerpilot.tar.gz \
    && curl -Lso /tmp/rethinkdb-health.tar.gz \ 
        "https://github.com/docketbook/rethinkdb-containerpilot-health/releases/download/0.1/rethinkdb-health-0.1-linux.tar.gz" \
    && tar zxf /tmp/rethinkdb-health.tar.gz -C /usr/local/bin \
    && rm /tmp/rethinkdb-health.tar.gz

# configure ContainerPilot and RethinkDB
COPY etc/* /etc/

# override the parent entrypoint
ENTRYPOINT []

EXPOSE 29015 28015 8080

VOLUME ["/data"]

WORKDIR /data

# use --console to get error logs to stderr
CMD [ "containerpilot", \
      "rethinkdb", \
      "--config-file", \
      "/etc/rethink.conf", \
      "--bind", \
      "all" \
]
