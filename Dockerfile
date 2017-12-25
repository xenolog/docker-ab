FROM alpine:3.6
LABEL maintainer="Sergey Vasilenko <svasilenko@mirantis.com>"

# Set the minimum Docker API version required for libnetwork.
ENV DOCKER_API_VERSION 1.21

RUN mkdir -p /var/lib/agent_input /var/lib/agent_output \
  && apk update \
  && apk add curl ca-certificates apache2-utils python3 py3-yaml \
  && pip3 install yaql \
  && mkdir -p /tmp/src

# Copy in the filesystem
COPY root/ /
COPY src/ /tmp/src/

RUN pip3 install /tmp/src/ab-parse/ \
  && pip3 install /tmp/src/sc-runner/ \
  && rm -rf /tmp/src && rm -rf /var/cache/apk/*

CMD ["start_ab"]
# should be latest for proper versioning
RUN date +%Y%m%d-%H:%M:%S-%Z > /buildinfo.txt
