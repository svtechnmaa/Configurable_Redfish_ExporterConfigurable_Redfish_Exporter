# Compile redfish_exporter
FROM python:3.12.7-alpine3.20 as build

LABEL Name=builder
LABEL appVersion=${appVersion}
LABEL maintainer=${maintainer}

ENV TZ=Asia/Ho_Chi_Minh

COPY ./src /opt/Configurable_Redfish_Exporter/src
COPY MANIFEST.in /opt/Configurable_Redfish_Exporter/MANIFEST.in
COPY setup.py /opt/Configurable_Redfish_Exporter/setup.py

RUN pip3 install setuptools
WORKDIR /opt/Configurable_Redfish_Exporter
RUN python3 setup.py sdist --formats=gztar

FROM python:3.12.7-alpine3.20

LABEL Name=redfish_exporter
LABEL appVersion=${appVersion}
LABEL maintainer=${maintainer}

ENV TZ=Asia/Ho_Chi_Minh

# COPY --from=build /opt/Configurable_Redfish_Exporter/src/redfish_exporter/templates /opt/Configurable_Redfish_Exporter/templates
COPY --from=build /opt/Configurable_Redfish_Exporter/dist/*.tar.gz /tmp/redfish_exporter/physical-exporter.tar.gz
RUN apk add tzdata && \
    echo $TZ > /etc/timezone && \
    pip install --no-cache-dir /tmp/redfish_exporter/physical-exporter.tar.gz && \
    rm -rf /tmp/* && \
    mkdir -p /opt/redfish_exporter && \
    ln -s /usr/local/lib/python3.12/site-packages/redfish_collector/core/templates /opt/redfish_exporter/templates
ENTRYPOINT ["redfish-exporter"]
EXPOSE 9814