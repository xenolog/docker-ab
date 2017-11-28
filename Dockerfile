FROM alpine:3.6
MAINTAINER Sergey Vasilenko <svasilenko@mirantis.com>

# Set the minimum Docker API version required for libnetwork.
ENV DOCKER_API_VERSION 1.21

RUN apk update \
  && apk --no-cache add curl ca-certificates apache2-utils python2 \
  && rm -rf /var/cache/apk/*

# Copy in the filesystem
COPY root/ /

CMD ["start_ab"]
RUN date +%Y%m%d-%H:%M:%S-%Z > /buildinfo.txt
