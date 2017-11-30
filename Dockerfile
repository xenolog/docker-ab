FROM alpine:3.6
MAINTAINER Sergey Vasilenko <svasilenko@mirantis.com>

# Set the minimum Docker API version required for libnetwork.
ENV DOCKER_API_VERSION 1.21

RUN apk update \
  && apk --no-cache add curl ca-certificates apache2-utils python3

# Copy in the filesystem
COPY root/ /
COPY src/ /tmp/

RUN pip3 install /tmp/ab-parse/ \
  && pip3 install /tmp/json2env/ \
  && pip3 install /tmp/gen_json_adder/ \
  && rm -rf /tmp/* && rm -rf /var/cache/apk/*

CMD ["start_ab"]
# should be latest for proper versioning
RUN date +%Y%m%d-%H:%M:%S-%Z > /buildinfo.txt
