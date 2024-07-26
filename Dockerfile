# Compile redfish_exporter
FROM alpine:3.14 as build

LABEL Name=builder
LABEL Version=1.0.0
LABEL maintainer="Freezing"

ENV TZ=Asia/Ho_Chi_Minh

COPY ./src /opt/Configurable_Redfish_Exporter/src
COPY setup.py /opt/Configurable_Redfish_Exporter/setup.py

RUN apk add py3-pip && \
    pip3 install setuptools
WORKDIR /opt/Configurable_Redfish_Exporter
RUN python3 setup.py sdist --formats=gztar

FROM alpine:3.14

LABEL Name=redfish_exporter
LABEL Version=1.0.0
LABEL maintainer="Freezing"

ENV TZ=Asia/Ho_Chi_Minh

COPY --from=build /opt/Configurable_Redfish_Exporter/src/redfish_exporter/templates /opt/Configurable_Redfish_Exporter/templates
COPY --from=build /opt/Configurable_Redfish_Exporter/dist/*.tar.gz /tmp/redfish_exporter/physical-exporter.tar.gz
RUN apk add tzdata py3-pip && \
    pip install --no-cache-dir /tmp/redfish_exporter/physical-exporter.tar.gz && \
    rm -rf /tmp/*
ENTRYPOINT ["redfish-exporter"]
EXPOSE 9814

# LABEL maintainer="Freezing"
# LABEL Name=tacacsgui
# LABEL Version=1.5.0
# ARG DEBIAN_FRONTEND=noninteractive
# ENV TZ=Asia/Ho_Chi_Minh

# COPY --from=build /var/lib/tac_plus /var/lib/tac_plus
# COPY ./src /opt/tacacsgui
# COPY configs/init.sh /opt/init.sh
# COPY configs/default_vars.sh /opt/tgui_data/default_vars.sh
# COPY configs/apache2/tacacsgui.local.conf /tmp/tacacsgui.local.conf
# COPY configs/apache2/tacacsgui.local-ssl.conf /tmp/tacacsgui.local-ssl.conf

# RUN echo 'root:juniper@123' | chpasswd && \
#     sed -i -e 's/archive.ubuntu.com/vn.archive.ubuntu.com/g' /etc/apt/sources.list && \
#     apt update && \
#     cp /var/lib/tac_plus/sbin/tac_plus /usr/sbin/tac_plus && \
#     cp /var/lib/tac_plus/sbin/tac_plus /usr/local/sbin/tac_plus && \
#     apt install -y sudo nano tcpdump tzdata libapache2-mod-xsendfile libbind-dev libpcre3-dev:amd64 libdigest-md5-perl libnet-ldap-perl libio-socket-ssl-perl php7.4 php7.4-common php7.4-cli php7.4-fpm php7.4-curl php7.4-dev php7.4-gd php7.4-mbstring php7.4-zip php7.4-mysql php7.4-xml libapache2-mod-php7.4 php7.4-ldap python3-mysqldb libmysqlclient-dev python3-dev curl unzip python3-pip mariadb-client && \
#     pip install --no-cache-dir sqlalchemy alembic mysqlclient pexpect pyyaml argparse pyotp gitpython && \
#     rm -rf /var/cache/apt/*  && \
#     chmod 775 /opt/init.sh && \
#     /bin/bash /opt/init.sh && \
#     rm -f /opt/init.sh

# EXPOSE 49 4443

# ENTRYPOINT ["apache2ctl","-D","FOREGROUND"]