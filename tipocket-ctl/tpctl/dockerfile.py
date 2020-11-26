local_dockerfile = '''
FROM pingcap/alpine-glibc

RUN mkdir -p /config
COPY bin/ /bin/
COPY config /config

EXPOSE 8080
'''
