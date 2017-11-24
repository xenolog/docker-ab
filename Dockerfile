FROM alpine:latest
MAINTAINER Sergey Vasilenko <svasilenko@mirantis.com>

# Set the minimum Docker API version required for libnetwork.
ENV DOCKER_API_VERSION 1.21
EXPOSE 179 180

RUN apk update \
  && apk --no-cache add curl ca-certificates apache2-utils \
  && apk add --no-cache --repository "http://alpine.gliderlabs.com/alpine/edge/community" runit \
  && rm -rf /var/cache/apk/* && date +%Y%m%d-%H:%M:%S-%Z > /buildinfo.txt

# Copy in the filesystem
COPY root/ /

CMD ["start_runit"]