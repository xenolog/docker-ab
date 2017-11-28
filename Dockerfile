FROM alpine:3.6
MAINTAINER Sergey Vasilenko <svasilenko@mirantis.com>

# Set the minimum Docker API version required for libnetwork.
ENV DOCKER_API_VERSION 1.21

RUN apk update \
  && apk --no-cache add curl ca-certificates apache2-utils python2 vim \
  && rm -rf /var/cache/apk/*

# Copy in the filesystem
COPY root/ /
COPY src/json2env/json2env.py              /usr/bin/json2env
COPY src/gen_json_adder/gen_json_adder.py  /usr/bin/gen_json_adder
COPY src/ab-parse/ab-to-json/ab-to-json.py /usr/bin/ab-to-json

CMD ["start_ab"]
RUN date +%Y%m%d-%H:%M:%S-%Z > /buildinfo.txt
