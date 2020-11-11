FROM pingcap/alpine-glibc

RUN mkdir -p /config && mkdir -p /resources
COPY bin/ /bin/
COPY config /config
COPY resources /resources

EXPOSE 8080
