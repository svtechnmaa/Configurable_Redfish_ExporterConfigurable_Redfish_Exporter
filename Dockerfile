# Compile redfish_exporter
FROM alpine:3.14 as build

LABEL Name=builder
LABEL appVersion=${appVersion}
LABEL maintainer=${maintainer}

ENV TZ=Asia/Ho_Chi_Minh

COPY ./src /opt/Configurable_Redfish_Exporter/src
COPY setup.py /opt/Configurable_Redfish_Exporter/setup.py

RUN apk add py3-pip && \
    pip3 install setuptools
WORKDIR /opt/Configurable_Redfish_Exporter
RUN python3 setup.py sdist --formats=gztar

FROM alpine:3.14

LABEL Name=redfish_exporter
LABEL appVersion=${appVersion}
LABEL maintainer=${maintainer}

ENV TZ=Asia/Ho_Chi_Minh

COPY --from=build /opt/Configurable_Redfish_Exporter/src/redfish_exporter/templates /opt/Configurable_Redfish_Exporter/templates
COPY --from=build /opt/Configurable_Redfish_Exporter/dist/*.tar.gz /tmp/redfish_exporter/physical-exporter.tar.gz
RUN apk add tzdata py3-pip && \
    echo $TZ > /etc/timezone && \
    pip install --no-cache-dir /tmp/redfish_exporter/physical-exporter.tar.gz && \
    rm -rf /tmp/*
ENTRYPOINT ["redfish-exporter"]
EXPOSE 9814