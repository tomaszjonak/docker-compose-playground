FROM golang:1.9-alpine as confd

ARG CONFD_VERSION=0.14.0

ADD https://github.com/kelseyhightower/confd/archive/v${CONFD_VERSION}.tar.gz /tmp/

RUN apk add --no-cache \
    bzip2 \
    make && \
  mkdir -p /go/src/github.com/kelseyhightower/confd && \
  cd /go/src/github.com/kelseyhightower/confd && \
  tar --strip-components=1 -zxf /tmp/v${CONFD_VERSION}.tar.gz && \
  go install github.com/kelseyhightower/confd && \
  rm -rf /tmp/v${CONFD_VERSION}.tar.gz

from nginx:1.13.8-alpine

COPY --from=confd /go/bin/confd /usr/local/bin/confd
COPY confd /etc/confd
COPY nginx_startup.sh nginx_startup.sh

CMD ["/bin/sh", "-c", "./nginx_startup.sh"]

